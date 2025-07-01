from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from models import Todo
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import decode_access_token

router = APIRouter(
    tags=["todo"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(decode_access_token)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(ge=0, le=10)
    completed: bool


@router.get("/todo/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    return db.query(Todo).filter(Todo.owner_id == user["id"]).all()


@router.get("/todo/{id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    queryset = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user["id"]).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    queryset = Todo(**todo_request.model_dump(), owner_id=user["id"])

    db.add(queryset)
    db.commit()
    return status.HTTP_201_CREATED


@router.put("/todo/{id}", status_code=status.HTTP_200_OK)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    id: int = Path(gt=0),
):
    queryset = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user["id"]).first()
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        setattr(queryset, "title", todo_request.title)
        setattr(queryset, "description", todo_request.description)
        setattr(queryset, "priority", todo_request.priority)
        setattr(queryset, "completed", todo_request.completed)
        setattr(queryset, "owner_id", user["id"])

    db.add(queryset)
    db.commit()
    return status.HTTP_200_OK


@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    queryset = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user["id"]).first()
    if queryset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        db.query(Todo).filter(Todo.id == id).delete()
        db.commit()

    return status.HTTP_204_NO_CONTENT
