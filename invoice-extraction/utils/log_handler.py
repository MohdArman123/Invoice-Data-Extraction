import sys
from fastapi import Response, status
from config import settings
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from api_messages_and_codes.invoice import api_messages, api_codes

async def prepare_response(
    status_flag: bool,
    message: str = None,
    code: str = None,
    **kwargs
) -> dict:
    """
    Create a standardized response dictionary
    
    Args:
        status_flag: The status of the response (True/False)
        message: A message string for the response
        code: A code string for the response
        kwargs: Additional key-value pairs to include in the response
    
    Returns:
        A dictionary containing the response data
    """
    response = {
        'status': status_flag,
        'message': message,
        'code': code if settings.DEBUG else None
    }
    
    # Add any additional key-value pairs
    response.update(kwargs)
    
    return response

async def handle_db_exceptions(exception, response: Response = None):
    """
    Handle database exceptions and return standardized error responses
    
    Args:
        exception: The exception that occurred
        response: FastAPI Response object to set status codes
    
    Returns:
        dict: A standardized error response
    """
    debug = settings.DEBUG
    error_type = type(exception)
    line_info = f' | line: {sys.exc_info()[2].tb_lineno}' if debug else ''
    
    if error_type == IntegrityError:
        # 409 Conflict: Data conflict (e.g., unique constraint violation)
        if response:
            response.status_code = status.HTTP_409_CONFLICT
        error_message = str(exception) + line_info if debug else api_messages.INTERNAL_SERVER_ERROR
        return await prepare_response(False, error_message, api_codes.INTERNAL_SERVER_ERROR)
    
    elif error_type == OperationalError:
        # 503 Service Unavailable: Database connection issues
        if response:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_message = str(exception) + line_info if debug else api_messages.INTERNAL_SERVER_ERROR
        return await prepare_response(False, error_message, api_codes.INTERNAL_SERVER_ERROR)
    
    elif error_type == SQLAlchemyError:
        # 500 Internal Server Error: General SQLAlchemy errors
        if response:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_message = str(exception) + line_info if debug else api_messages.INTERNAL_SERVER_ERROR
        return await prepare_response(False, error_message, api_codes.INTERNAL_SERVER_ERROR)
    
    else:
        # 500 Internal Server Error: Any other exceptions
        if response:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_message = str(exception) + line_info if debug else api_messages.INTERNAL_SERVER_ERROR
        return await prepare_response(False, error_message, api_codes.INTERNAL_SERVER_ERROR)