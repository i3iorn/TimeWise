from typing import Union

from fastapi import FastAPI

from src.timewise import TimeWise

app = FastAPI()
timewise = TimeWise()


@app.get("/")
def read_root():
    return timewise.version