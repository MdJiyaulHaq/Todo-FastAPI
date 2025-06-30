from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
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
