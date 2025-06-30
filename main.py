from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
import models
from models import Todo
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(ge=0, le=10)
    completed: bool


@app.get("/todo/", status_code=status.HTTP_200_OK)
async def get_all_todos(db: db_dependency):
    return db.query(Todo).all()


@app.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, id: int = Path(gt=0)):
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    queryset = Todo(**todo_request.model_dump())

    db.add(queryset)
    db.commit()
    return status.HTTP_201_CREATED


@app.put("/todo/{id}", status_code=status.HTTP_200_OK)
async def update_todo(
    db: db_dependency, todo_request: TodoRequest, id: int = Path(gt=0)
):
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        setattr(queryset, "title", todo_request.title)
        setattr(queryset, "description", todo_request.description)
        setattr(queryset, "priority", todo_request.priority)
        setattr(queryset, "completed", todo_request.completed)

    db.add(queryset)
    db.commit()
    return status.HTTP_200_OK


@app.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, id: int = Path(gt=0)):
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        db.query(Todo).filter(Todo.id == id).delete()
        db.commit()

    return status.HTTP_204_NO_CONTENT
