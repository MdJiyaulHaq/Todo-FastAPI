from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from models import Todo, User
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    tags=["users"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/users/", status_code=status.HTTP_200_OK)
async def get_user(
    user: user_dependency,
    db: db_dependency,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    queryset = db.query(User).filter(User.id == user["id"]).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
