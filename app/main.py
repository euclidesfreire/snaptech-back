from fastapi import FastAPI
from database import create_db_and_tables
from .routers import articles, users

app = FastAPI()

app.include_router(users.router)
app.include_router(articles.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}