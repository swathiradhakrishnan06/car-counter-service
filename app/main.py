from app.routers import cars
from fastapi import FastAPI

app = FastAPI()

app.include_router(cars.router)
