# main.py
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Rocket Influence Custom REST API server is up!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

