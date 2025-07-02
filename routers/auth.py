from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from fastapi import Request
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from database import SessionLocal
from models import Users
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["auth"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
templates = Jinja2Templates(directory="templates")


@router.get("/auth/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(
        password, getattr(user, "hashed_password", None)
    ):
        return None
    return user


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = ")7vv&q)!f+*xf)*hpb^qv*&nx%=ip0^nk0xb1vty&07as1n1l0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(
    username: str,
    user_id: int,
    role: str,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
):
    expiration = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expiration, "sub": username, "id": user_id, "role": role}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        role = payload.get("role")
        if (
            not isinstance(username, str)
            or user_id is None
            or not isinstance(role, str)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user",
            )
        return {"username": username, "id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    first_name: str = Field(min_length=3, max_length=100)
    last_name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    role: str = Field()
    phone_number: str = Field(min_length=10, max_length=15)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.get("/auth")
async def get_user():
    return "hello world"


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number,
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def create_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
    user: Users = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(username=user.username, user_id=user.id, role=user.role)  # type: ignore
    return {"access_token": access_token, "token_type": "bearer"}
