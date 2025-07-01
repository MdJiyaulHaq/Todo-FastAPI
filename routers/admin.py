from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from models import Todo
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

router = APIRouter(
    tags=["admin"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/admin/todo/", status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependency, db: db_dependency):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return db.query(Todo).all()


@router.get("/admin/todo/{id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/admin/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    queryset = db.query(Todo).filter(Todo.id == id).first()
    if queryset is not None:
        db.delete(queryset)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
