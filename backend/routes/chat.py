"""
Chat API routes with SSE streaming support.
"""
import json
import base64
from typing import Any
from datetime import datetime
from flask import Blueprint, Response, request, stream_with_context
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.protobuf import json_format
from google.protobuf.message import Message as ProtobufMessage

from config import Config
from models import FUNCTION_TOOLS
from prompts import SYSTEM_PROMPT
from services import DocumentService, conversation_service
from utils import create_sse_response


# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


def convert_to_serializable(obj: Any, depth: int = 0, max_depth: int = 20, visited: set = None) -> Any:
    """
    Recursively convert objects to JSON-serializable format.

    Handles Gemini's MapComposite, protobuf messages, and other non-serializable objects.
    Prevents infinite recursion with depth limiting and circular reference tracking.

    Args:
        obj: Object to convert
        depth: Current recursion depth
        max_depth: Maximum allowed recursion depth
        visited: Set of object IDs already visited (for circular reference detection)

    Returns:
        JSON-serializable version of the object
    """
    # Prevent infinite recursion
    if depth > max_depth:
        return f"<max_depth_exceeded: {type(obj).__name__}>"

    # Initialize visited set on first call
    if visited is None:
        visited = set()

    # Check for primitive types first
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # Check for circular references using object ID
    obj_id = id(obj)
    if obj_id in visited:
        return f"<circular_ref: {type(obj).__name__}>"

    # Add to visited set
    visited.add(obj_id)

    try:
        # Handle protobuf messages first (before dict-like checks)
        if isinstance(obj, ProtobufMessage):
            return json_format.MessageToDict(obj)
        
        # Handle lists and tuples
        if isinstance(obj, (list, tuple)):
            return [convert_to_serializable(item, depth + 1, max_depth, visited) for item in obj]

        # Handle regular dicts
        if isinstance(obj, dict):
            return {str(key): convert_to_serializable(value, depth + 1, max_depth, visited)
                    for key, value in obj.items()}

        # Handle MapComposite and similar dict-like objects (but not regular objects)
        # Check for keys() and __getitem__ to identify dict-like objects
        if hasattr(obj, 'keys') and hasattr(obj, '__getitem__') and not isinstance(obj, type):
            try:
                # First try to convert via dict() which works for MapComposite
                if hasattr(obj, 'items'):
                    result = {}
                    for key, value in obj.items():
                        result[str(key)] = convert_to_serializable(value, depth + 1, max_depth, visited)
                    return result
                else:
                    return {str(key): convert_to_serializable(obj[key], depth + 1, max_depth, visited)
                            for key in obj.keys()}
            except (TypeError, AttributeError):
                # Some dict-like objects may not support iteration or key access; fall through to next handler
                pass

        # Handle objects with __dict__ (but avoid infinite recursion)
        if hasattr(obj, '__dict__') and not isinstance(obj, type):
            try:
                obj_dict = obj.__dict__
                # Only recurse if it's a regular dict
                if isinstance(obj_dict, dict):
                    return convert_to_serializable(obj_dict, depth + 1, max_depth, visited)
            except (TypeError, AttributeError):
                # Some objects may not have a serializable __dict__; fall back to string conversion below
                pass

        # Fallback: convert to string
        return str(obj)
    finally:
        # No cleanup needed; visited set persists for entire traversal
        pass


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
                system_instruction=SYSTEM_PROMPT,
                generation_config=GenerationConfig(
                    temperature=0.0
                )
            )

            # Get conversation history (exclude the current message)
            history = conversation_service.get_history(conversation_id)[:-1]

            # Create chat session
            chat_session = model.start_chat(history=history)

            # Send message and stream response
            response = chat_session.send_message(user_message, stream=True)

            accumulated_text = ""
            
            # Loop to handle chained function calls (e.g. get_date -> generate_document)
            while True:
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

                # If no function calls, we are done with this turn
                if not function_calls:
                    break

                # Prepare function responses
                function_response_parts = []

                for func_call in function_calls:
                    func_name = func_call.name
                    # Convert args to JSON-serializable format
                    func_args = convert_to_serializable(func_call.args)

                    # Validate that func_args is a dict before using
                    if not isinstance(func_args, dict):
                        func_args = {}

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

                    # Yield document if generated (PDF as base64)
                    if function_result.get('pdf_base64'):
                        yield create_sse_response('document', {
                            'pdf_base64': function_result.get('pdf_base64_preview', function_result['pdf_base64']),
                            'pdf_base64_download': function_result.get('pdf_base64_download', function_result['pdf_base64']),
                            'changes': function_result.get('changes')
                        })

                    # Add to response parts
                    function_response_parts.append({
                        'function_response': {
                            'name': func_name,
                            'response': function_result
                        }
                    })

                # Send all function results back to the model
                response = chat_session.send_message({
                    'role': 'function',
                    'parts': function_response_parts
                }, stream=True)
                
                # The loop will now process the model's response to these function results

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
            error_msg = f"Error processing message: {str(e)}. Please try again or check your connection."
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
            # Generate document (returns PDF bytes and document data)
            pdf_bytes, doc_data_dict = DocumentService.generate(doc_type, doc_data)

            # Store document
            conversation_service.set_document(conversation_id, pdf_bytes, doc_data_dict)

            # Convert PDF to base64 for transmission
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

            return {
                'status': 'success',
                'message': 'Document generated successfully',
                'pdf_base64': pdf_base64,
                'pdf_base64_preview': pdf_base64,
                'pdf_base64_download': pdf_base64
            }
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    elif func_name == 'apply_edits':
        # Get current document data (not the PDF)
        doc_data = conversation_service.get_document_data(conversation_id)

        if doc_data:
            edit_type = func_args.get('edit_type', '')
            field_name = func_args.get('field_name', '')
            new_value = func_args.get('new_value', '')

            try:
                # Apply edit and regenerate PDF
                pdf_preview, pdf_download, updated_doc_data, changes = DocumentService.apply_edit(
                    doc_data,
                    edit_type,
                    field_name,
                    new_value
                )

                # Store updated document (store the download version as the "official" one)
                conversation_service.set_document(conversation_id, pdf_download, updated_doc_data)

                # Convert PDF to base64 for transmission
                pdf_base64_preview = base64.b64encode(pdf_preview).decode('utf-8')
                pdf_base64_download = base64.b64encode(pdf_download).decode('utf-8')

                return {
                    'status': 'success',
                    'message': f'Document updated: {changes}',
                    'changes': changes,
                    'pdf_base64': pdf_base64_preview, # Legacy support if needed
                    'pdf_base64_preview': pdf_base64_preview,
                    'pdf_base64_download': pdf_base64_download
                }
            except ValueError as e:
                return {
                    'status': 'error',
                    'message': str(e)
                }
        else:
            return {
                'status': 'error',
                'message': 'No document exists to edit. Please generate a document first.'
            }

    elif func_name == 'get_current_date':
        # Just return the current date, let the LLM handle relative calculations
        today = datetime.now()
        return {
            'status': 'success',
            'date': today.strftime('%Y-%m-%d'),
            'description': 'Current date'
        }

    return {
        'status': 'error',
        'message': f'Unknown function: {func_name}'
    }
