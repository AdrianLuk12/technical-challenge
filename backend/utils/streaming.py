"""
SSE streaming utilities.
"""
import json
from typing import Dict, Any


def create_sse_response(event_type: str, data: Dict[str, Any]) -> str:
    """
    Create a formatted SSE response.

    Args:
        event_type: Type of event ('text', 'document', 'function_call', 'done', 'error')
        data: Additional data for the event

    Returns:
        Formatted SSE message

    Raises:
        TypeError: If data contains non-JSON-serializable objects
    """
    payload = {'type': event_type, **data}
    try:
        return f"data: {json.dumps(payload)}\n\n"
    except TypeError as e:
        # Log the error with details about what failed to serialize
        error_msg = f"Failed to serialize SSE payload: {e}. Event type: {event_type}"
        print(f"ERROR: {error_msg}")
        # Return an error event instead
        error_payload = {'type': 'error', 'content': error_msg}
        return f"data: {json.dumps(error_payload)}\n\n"
