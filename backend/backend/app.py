from fastapi import FastAPI
from .routers import expenses
from .routers import users

app = FastAPI()
app.include_router(expenses.router)
app.include_router(users.router)