from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from fastapi.params import Body
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from models import Todo
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    tags=["todo"],
    prefix="/todos",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(ge=0, le=10)
    completed: bool


def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page")
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


# Todo pages
@router.get("/todo-page")
async def todo_page(request: Request, db: db_dependency):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return redirect_to_login()
    try:
        user = await get_current_user(access_token)
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user["id"]).all()
        return templates.TemplateResponse(
            "todo.html", {"request": request, "todos": todos, "user": user}
        )
    except Exception:
        return redirect_to_login()


@router.get("/add-todo-page")
async def add_todo_page(request: Request, db: db_dependency):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return redirect_to_login()
    try:
        user = await get_current_user(access_token)
        if user is None:
            return redirect_to_login()
        return templates.TemplateResponse(
            "add-todo.html", {"request": request, "user": user}
        )
    except Exception:
        return redirect_to_login()


@router.get("/edit-todo-page/{id}")
async def edit_todo_page(request: Request, db: db_dependency, id: int = Path(gt=0)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return redirect_to_login()
    try:
        user = await get_current_user(access_token)
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == id, Todo.owner_id == user["id"]).first()
        if todo is None:
            return redirect_to_login()
        return templates.TemplateResponse(
            "edit-todo.html", {"request": request, "user": user, "todo": todo}
        )
    except Exception:
        return redirect_to_login()


# Todo endpoints
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
