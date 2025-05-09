from typing import Union

from fastapi import FastAPI
from .routers import cards

app = FastAPI()

app.include_router(cards.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
