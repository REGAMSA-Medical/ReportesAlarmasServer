from ..repositories.common import list_items, list_items_by_category, get_item_by_id, create_item, delete_item
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from ..utils.responses import NotFoundItemsResponse, NotFoundItemResponse, GetItemResponse, CreateItemResponse, NotCreatedItemErrorResponse, ListItemsResponse, DeletedItemResponse, DeleteItemErrorResponse
from ..decorators.common import handle_exceptions

@handle_exceptions
async def list_items_service(db:AsyncSession, model:BaseModel, serializer:BaseModel):
    items = await list_items(db, model)
    serialized_items = [serializer.from_orm(item) for item in items]
    if len(items) < 1:
        return NotFoundItemsResponse()
    return ListItemsResponse(items=serialized_items)

@handle_exceptions
async def list_items_by_category_service(db:AsyncSession, model:BaseModel, serializer:BaseModel, category_key:str, category_value:str):
    items = await list_items_by_category(db, model, category_key, category_value)
    serialized_items = [serializer.from_orm(item) for item in items]
    if len(items) < 1:
        return NotFoundItemsResponse()
    return ListItemsResponse(items=serialized_items)

@handle_exceptions
async def list_items_by_model_mapping_service(db:AsyncSession, models:dict[str:BaseModel], model_selector:str, serializers:dict[str:BaseModel], serializer_selector:str):
    default_model = next(iter(models.values()))
    default_serializer = next(iter(serializers.values()))

    model = models.get(model_selector, default_model)
    serializer = serializers.get(serializer_selector, default_serializer)

    items = await list_items(db, model)
    serialized_items = [serializer.from_orm(item) for item in items]
    
    if len(items) < 1:
        return NotFoundItemsResponse()
    return ListItemsResponse(items=serialized_items)

@handle_exceptions
async def get_item_by_id_service(db:AsyncSession, model:BaseModel, serializer:BaseModel, id:int):
    item = await get_item_by_id(db, model, id)
    serialized_item = serializer.from_orm(item)
    if not item:
        return NotFoundItemResponse()
    return GetItemResponse(serialized_item)

@handle_exceptions
async def create_item_service(db:AsyncSession, model:BaseModel, serializer:BaseModel, item_values:BaseModel):
    new_item = await create_item(db=db, model=model, item_values=item_values)
    serialized_new_item = serializer.from_orm(new_item)
    if not new_item:
        return NotCreatedItemErrorResponse()
    return CreateItemResponse(item=serialized_new_item)

@handle_exceptions
async def delete_item_service(db:AsyncSession, model:BaseModel, serializer:BaseModel, id:int):
    item_to_delete = await get_item_by_id(db=db, model=model, id=id)
    if item_to_delete is None:
        return NotFoundItemResponse()
    deleted_item = await delete_item(db=db, model=model, id=id)
    serialized_deleted_item = serializer.from_orm(deleted_item)
    if deleted_item is None:
        return DeletedItemResponse()
    else:
        return DeleteItemErrorResponse(item=serialized_deleted_item)

@handle_exceptions
async def get_dictionary_service(dictionary:dict):
    if len(dictionary.keys)<1:
        return NotFoundItemResponse
    return GetItemResponse(item=dictionary)

@handle_exceptions
def get_items_from_datafile_service(filename:str):
    import pandas as pd
    datasources_path = 'app/datasources/'

    if filename.endswith('csv'):
        df = pd.read_csv(f'{datasources_path}{filename}')
    elif filename.endswith(['xlsx', 'xls']):
        df = pd.read_excel(f'{datasources_path}{filename}')
    else:
        df = None
        raise ValueError('Provided file must be of csv, xlsx or xls type')
    
    return df.to_dict(orient='records')