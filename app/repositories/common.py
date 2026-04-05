from typing import Type, List
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

async def get_item_by_id(db:AsyncSession, model:Type[DeclarativeMeta], id:int):
    result = await db.execute(select(model).where(model.id == id))
    return result.scalars().first()

async def list_items(db:AsyncSession, model:Type[DeclarativeMeta]) -> List:
    result = await db.execute(select(model))
    return result.scalars().all()

async def R_list_items_where_column_equals_value(db:AsyncSession, model:Type[DeclarativeMeta], column:str, value:str|bool|int|float) -> List:
    if not hasattr(model, column):
        raise ValueError(f'Invalid column name: {column}')
    
    column_attr = getattr(model, column)

    result = await db.execute(select(model).where(column_attr==value))
    return result.scalars().all()

async def R_list_items_where_column_differs_value(db:AsyncSession, model:Type[DeclarativeMeta], column:str, value:str|bool|int|float) -> List:
    if not hasattr(model, column):
        raise ValueError(f'Invalid column name: {column}')
    
    column_attr = getattr(model, column)

    result = await db.execute(select(model).where(column_attr!=value))
    return result.scalars().all()

async def create_item(db:AsyncSession, model:Type[DeclarativeMeta], item_values) -> Type[DeclarativeMeta]:
    new_item = model(**item_values.model_dump())
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item

async def delete_item(db:AsyncSession, model:Type[DeclarativeMeta], id:int):
    await db.execute(delete(model).where(model.id==id))
    await db.commit()
    deleted_item = await db.execute(select(model).where(model.id==id))
    
    if deleted_item:
        return deleted_item.scalars().first()
    return None