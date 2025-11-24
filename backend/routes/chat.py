"""
Chat API routes with SSE streaming support.
"""
import json
from typing import Any
from flask import Blueprint, Response, request, stream_with_context
import google.generativeai as genai

from config import Config
from models import FUNCTION_TOOLS
from prompts import SYSTEM_PROMPT
from services import DocumentService, conversation_service
from utils import create_sse_response


# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


def convert_to_serializable(obj: Any) -> Any:
    """
    Recursively convert objects to JSON-serializable format.

    Handles Gemini's MapComposite and other non-serializable objects.

    Args:
        obj: Object to convert

    Returns:
        JSON-serializable version of the object
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]

    if isinstance(obj, dict):
        return {str(key): convert_to_serializable(value) for key, value in obj.items()}

    # Handle MapComposite and similar objects by converting to dict
    if hasattr(obj, '__iter__') and hasattr(obj, 'keys'):
        return {str(key): convert_to_serializable(obj[key]) for key in obj.keys()}

    # Handle other objects with dict representation
    if hasattr(obj, '__dict__'):
        return convert_to_serializable(obj.__dict__)

    # Fallback: convert to string
    return str(obj)


@chat_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {'status': 'healthy', 'message': 'Legal Document Assistant API is running'}


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint with SSE streaming.

    Request JSON:
        {
            "message": "User message",
            "conversation_id": "optional-uuid"
        }

    Response: SSE stream with events:
        - type: text - Text chunk
        - type: function_call - Function being called
        - type: document - Generated/updated document
        - type: done - Conversation complete
        - type: error - Error occurred
    """
    data = request.json
    user_message = data.get('message', '')
    conversation_id = data.get('conversation_id')

    # Create new conversation if needed
    if not conversation_id or not conversation_service.conversation_exists(conversation_id):
        conversation_id = conversation_service.create_conversation()

    # Add user message to history
    conversation_service.add_message(conversation_id, 'user', user_message)

    def generate():
        """Generator function for SSE streaming."""
        try:
            # Initialize Gemini model
            model = genai.GenerativeModel(
                model_name=Config.GEMINI_MODEL,
                tools=FUNCTION_TOOLS,
                system_instruction=SYSTEM_PROMPT
            )

            # Get conversation history (exclude the current message)
            history = conversation_service.get_history(conversation_id)[:-1]

            # Create chat session
            chat_session = model.start_chat(history=history)

            # Send message and stream response
            response = chat_session.send_message(user_message, stream=True)

            accumulated_text = ""
            function_calls = []

            # Process streaming response
            for chunk in response:
                if chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        # Handle function calls
                        if hasattr(part, 'function_call') and part.function_call:
                            function_calls.append(part.function_call)
                        # Handle text
                        elif hasattr(part, 'text') and part.text:
                            accumulated_text += part.text
                            yield create_sse_response('text', {'content': part.text})

            # Handle function calls
            if function_calls:
                for func_call in function_calls:
                    func_name = func_call.name
                    # Convert args to JSON-serializable format
                    func_args = convert_to_serializable(func_call.args)

                    # Notify frontend about function call
                    yield create_sse_response('function_call', {
                        'function': func_name,
                        'args': func_args
                    })

                    # Execute function
                    function_result = execute_function(
                        conversation_id,
                        func_name,
                        func_args
                    )

                    # Yield document if generated
                    if function_result.get('document'):
                        yield create_sse_response('document', {
                            'content': function_result['document'],
                            'changes': function_result.get('changes')
                        })

                    # Continue conversation with function result
                    response2 = chat_session.send_message({
                        'role': 'function',
                        'parts': [{
                            'function_response': {
                                'name': func_name,
                                'response': function_result
                            }
                        }]
                    }, stream=True)

                    # Stream continuation
                    for chunk in response2:
                        if chunk.candidates[0].content.parts:
                            for part in chunk.candidates[0].content.parts:
                                if hasattr(part, 'text') and part.text:
                                    accumulated_text += part.text
                                    yield create_sse_response('text', {'content': part.text})

            # Store assistant response
            if accumulated_text:
                conversation_service.add_message(
                    conversation_id,
                    'model',
                    accumulated_text
                )

            # Send completion
            yield create_sse_response('done', {'conversation_id': conversation_id})

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield create_sse_response('error', {'content': error_msg})

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@chat_bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """
    Get conversation history and document.

    Args:
        conversation_id: Conversation ID

    Returns:
        JSON with conversation data or 404 error
    """
    conversation_data = conversation_service.get_conversation_data(conversation_id)

    if conversation_data:
        return conversation_data
    return {'error': 'Conversation not found'}, 404


@chat_bp.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """
    Delete conversation and associated data.

    Args:
        conversation_id: Conversation ID

    Returns:
        Success message or 404 error
    """
    if conversation_service.delete_conversation(conversation_id):
        return {'message': 'Conversation deleted'}
    return {'error': 'Conversation not found'}, 404


def execute_function(conversation_id: str, func_name: str, func_args: dict) -> dict:
    """
    Execute a function call from the LLM.

    Args:
        conversation_id: Conversation ID
        func_name: Function name
        func_args: Function arguments

    Returns:
        Function result dictionary
    """
    if func_name == 'extract_information':
        # Store extracted information
        return {
            'status': 'success',
            'message': 'Information extracted successfully',
            'data': func_args
        }

    elif func_name == 'generate_document':
        doc_type = func_args.get('document_type', '')
        doc_data = func_args.get('document_data', {})

        try:
            # Generate document
            generated_doc = DocumentService.generate(doc_type, doc_data)

            # Store document
            conversation_service.set_document(conversation_id, generated_doc)

            return {
                'status': 'success',
                'document': generated_doc
            }
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    elif func_name == 'apply_edits':
        current_doc = conversation_service.get_document(conversation_id)

        if current_doc:
            edit_type = func_args.get('edit_type', '')
            field_name = func_args.get('field_name', '')
            new_value = func_args.get('new_value', '')

            # Apply edit
            updated_doc, changes = DocumentService.apply_edit(
                current_doc,
                edit_type,
                field_name,
                new_value
            )

            # Store updated document
            conversation_service.set_document(conversation_id, updated_doc)

            return {
                'status': 'success',
                'changes': changes,
                'updated_document': updated_doc,
                'document': updated_doc
            }
        else:
            return {
                'status': 'error',
                'message': 'No document exists to edit. Please generate a document first.'
            }

    return {
        'status': 'error',
        'message': f'Unknown function: {func_name}'
    }
