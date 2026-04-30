from fastapi.responses import JSONResponse, Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from app.utils.logger import logger

# Success
def ListItemsResponse(items) -> JSONResponse:
    return JSONResponse(content={'items':jsonable_encoder(items), 'count':len(items)}, status_code=status.HTTP_200_OK)

def GetItemResponse(item) -> JSONResponse:
    return JSONResponse(content={'item':jsonable_encoder(item)}, status_code=status.HTTP_200_OK)

def CreateItemResponse(item) -> JSONResponse:
    return JSONResponse(content={'item':jsonable_encoder(item)}, status_code=status.HTTP_201_CREATED)

def DeletedItemResponse() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Error
def NotFoundItemResponse() -> JSONResponse:
    return JSONResponse(content={'error':'No item found'}, status_code=status.HTTP_404_NOT_FOUND)

def NotFoundItemsResponse() -> JSONResponse:
    return JSONResponse(content={'error':'No items found'}, status_code=status.HTTP_404_NOT_FOUND)

def InternalServerErrorResponse(error:Exception) -> JSONResponse:
    logger.error(f'Error: {error}')
    return JSONResponse(content={'error':str(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def NotCreatedItemErrorResponse(error:Exception) -> JSONResponse:
    logger.error(f'Bad Request Error: {error}')
    return JSONResponse(content={'error':f'Not created: {error}'}, status_code=status.HTTP_400_BAD_REQUEST)

def DeleteItemErrorResponse(item) -> JSONResponse:
    return JSONResponse(content={'error':f'It was not possible to delete this item: {jsonable_encoder(item)}'}, status_code=status.HTTP_409_CONFLICT)