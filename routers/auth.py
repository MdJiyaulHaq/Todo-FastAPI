from fastapi import APIRouter
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from models import User

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    role: str = Field()


@router.get("/auth")
async def get_user():
    return "hello world"


@router.post("/auth")
async def create_user(create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
    )

    return create_user_model
