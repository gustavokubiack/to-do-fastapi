from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def list_todos(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[models.Todo]:
    result = await db.execute(select(models.Todo).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_todo(db: AsyncSession, todo_id: int) -> models.Todo | None:
    result = await db.execute(select(models.Todo).where(models.Todo.id == todo_id))
    return result.scalar_one_or_none()


async def create_todo(db: AsyncSession, data: schemas.TodoCreate) -> models.Todo:
    todo = models.Todo(**data.model_dump())
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return todo


async def update_todo(
    db: AsyncSession, todo: models.Todo, data: schemas.TodoUpdate
) -> models.Todo:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    await db.commit()
    await db.refresh(todo)
    return todo


async def delete_todo(db: AsyncSession, todo: models.Todo) -> None:
    await db.delete(todo)
    await db.commit()
