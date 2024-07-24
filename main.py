from typing import Union

from fastapi import FastAPI

from src.timewise import TimeWise

app = FastAPI()


@app.get("/")
def read_root():
    return TimeWise().api.name


@app.get("/tasks")
def read_tasks():
    return TimeWise().api.tasks
