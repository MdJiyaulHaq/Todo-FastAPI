from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from models import Todo, Users
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(
    tags=["users"],
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserPasswordUpdate(BaseModel):
    password: str
    new_password: str = Field(min_length=8)


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
    queryset = db.query(Users).filter(Users.id == user["id"]).first()
    if queryset is not None:
        return queryset
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.put("/users/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, user_password_update: UserPasswordUpdate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    queryset = db.query(Users).filter(Users.id == user["id"]).first()
    if queryset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not bcrypt_context.verify(
        user_password_update.password, queryset.hashed_password  # type: ignore[union-attr]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )
    queryset.hashed_password = bcrypt_context.hash(user_password_update.new_password)  # type: ignore[union-attr]
    db.add(queryset)
    db.commit()
    return {"detail": "Password updated successfully"}
