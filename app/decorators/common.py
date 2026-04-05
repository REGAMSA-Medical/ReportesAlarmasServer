from functools import wraps
from ..utils.responses import InternalServerErrorResponse

def handle_http_exceptions(func):
    """
    Wrap an endpoint, try to execute it, and handle error automatically.
    Server Error is the default to be returned. 
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return InternalServerErrorResponse(e)
    return wrapper

def handle_exceptions(func):
    """
    Wrap a normal function, try to execute it, and handle error automatically.
    Error message is the default to be returned.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return f'Unexpected Error: {e}'
    return wrapper
