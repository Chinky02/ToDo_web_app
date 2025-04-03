from fastapi import FastAPI
from database import engine
from models.models import Base
from routers import users, tasks

Base.metadata.create_all(engine)


app = FastAPI()

app.include_router(users.router, prefix="/user")
app.include_router(tasks.router, prefix="/tasks")

@app.get("/")
def read_root():
    return {"Hello": "World"}

