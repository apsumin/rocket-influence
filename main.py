# main.py
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello World from Cloud Run!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

