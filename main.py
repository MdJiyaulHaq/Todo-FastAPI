from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import models
from database import engine
from routers import admin, auth, todo, users

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(admin.router)
app.include_router(users.router)
