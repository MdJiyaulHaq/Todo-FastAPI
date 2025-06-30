from typing import Annotated
from fastapi import FastAPI, Depends
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


@app.get("/")
async def get_all_todos(db: db_dependency):
    return db.query(Todo).all()
