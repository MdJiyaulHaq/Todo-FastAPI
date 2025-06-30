from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
import models
from models import Todo
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


@app.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(db: db_dependency):
    return db.query(Todo).all()


@app.get("/{id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, id: int):
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    queryset = Todo(**todo_request.model_dump())

    db.add(queryset)
    db.commit()
    return status.HTTP_201_CREATED
