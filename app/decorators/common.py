from functools import wraps
from ..utils.responses import InternalServerErrorResponse

def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return InternalServerErrorResponse(e)
    return wrapper
