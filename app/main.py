import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="To-Do List API",
    description="Uma API simples para gerenciar tarefas (to-do list).",
    version="1.0.0",
    lifespan=lifespan,
)


INDEX_HTML = os.path.join(os.path.dirname(__file__), "..", "static", "index.html")


@app.get("/")
async def root():
    if os.path.isfile(INDEX_HTML):
        return FileResponse(INDEX_HTML, media_type="text/html")
    return {
        "app": os.environ.get("APP_NAME", "to-do-fastapi"),
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/db-status")
async def db_status(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT NOW() as now"))
        row = result.one()
        return {"connected": True, "now": row.now.isoformat()}
    except Exception as e:
        return {"connected": False, "error": str(e)}


@app.get("/todos", response_model=list[schemas.TodoOut])
async def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await crud.list_todos(db, skip=skip, limit=limit)


@app.get("/todos/{todo_id}", response_model=schemas.TodoOut)
async def get_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo not found")
    return todo


@app.post("/todos", response_model=schemas.TodoOut, status_code=HTTPStatus.CREATED)
async def create_todo(data: schemas.TodoCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_todo(db, data)


@app.patch("/todos/{todo_id}", response_model=schemas.TodoOut)
async def update_todo(
    todo_id: int, data: schemas.TodoUpdate, db: AsyncSession = Depends(get_db)
):
    todo = await crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo not found")
    return await crud.update_todo(db, todo, data)


@app.delete("/todos/{todo_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Todo not found")
    await crud.delete_todo(db, todo)
