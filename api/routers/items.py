from fastapi import APIRouter, HTTPException, status
from ...db.database import client, db, collection
from contextlib import asynccontextmanager
from logging import info 
import logging
from typing import List, Dict

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def db_lifespan(app: APIRouter):
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
    
router: APIRouter = APIRouter(lifespan=db_lifespan)

@router.get("/find/one/{query}")
async def get_page(query):
    content = await collection.find_one(query)
    return content
    
@router.get("/find/all/", status_code=status.HTTP_200_OK)
async def get_pages(query={}):
    cursor = await collection.find(query)
    documents = []
    async for document in cursor:  # Use async for here
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        documents.append(document)
    
    if documents == []:
        raise HTTPException(status_code=204, detail="DataBase has not any data")
    else: return documents

@router.post("/content/{content}", status_code=status.HTTP_201_CREATED)
async def post_page(content):
    # Insert the structured result into MongoDB
    await collection.insert_one(content)
    return {"message": "Content and inserted"}

@router.post("/contents/{contents}", status_code=status.HTTP_201_CREATED)
async def post_pages(contents, skip_error:bool):    
    for index, content in enumerate(contents):
        if ("error" in content) and (skip_error == True): 
            contents.pop(index)
    await collection.insert_many(content)
        
    return {"message": "Page scraped and inserted"}

@router.delete("/delete/single/{query}")
async def get_pages(query):
    await collection.delete_one(query)
    return {"message": f"Query deleted successful: {query}"}

@router.delete("/delete/all/{query}")
async def get_pages(query):
    await collection.delete_many(query)
    return {"message": f"Querys deleted successful: {query}"}