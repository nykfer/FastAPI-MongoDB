from ..db.database import client, db, collection
from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging import info 
import logging

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = client
    app.database = db
    ping_response = await app.database.command("ping")
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        info("Connected to database cluster.")
    
    yield
    # Shutdown
    await app.mongodb_client.close()
    
app: FastAPI = FastAPI(lifespan=db_lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/page")
async def post_page():
    await collection.insert_one({"name": "John", "age": 30})