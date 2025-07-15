from fastapi import APIRouter, HTTPException, status
from ...db.database import client, db, collection
from contextlib import asynccontextmanager
from logging import info 
import logging
import json
from typing import Dict, List

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

@router.get("/find/one/{query_str}", status_code=status.HTTP_200_OK)
async def get_page(query_str:str):
    query: Dict = json.loads(query_str)
    document = await collection.find_one(query)
    if document is None:
        raise HTTPException(status_code=204, detail="Query doesn't match any data in the db")
    document["_id"] = str(document["_id"])
    return document
    
@router.get("/find/all/", status_code=status.HTTP_200_OK)
async def get_pages(query_str:str = "{}"):
    query: Dict = json.loads(query_str)
    cursor = collection.find(query)
    documents = []
    async for document in cursor:  # Use async for here
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        documents.append(document)
    
    if documents == []:
        raise HTTPException(status_code=204, detail="DataBase has not any data")
    else: return documents

@router.post("/content/{content_str}", status_code=status.HTTP_201_CREATED)
async def post_page(content_str: str):
    content: Dict = json.loads(content_str)
    # Insert the structured result into MongoDB
    await collection.insert_one(content)
    return {"message": "Content and inserted"}

@router.post("/contents/{contents_str}", status_code=status.HTTP_201_CREATED)
async def post_pages(contents_str, skip_error:bool):    
    contents_dict: List[Dict] = []
    for index, content in enumerate(contents_str):
        if ("error" in content) and (skip_error == True): 
            continue
        else:
            data: Dict = json.loads(content)
            contents_dict.append(data) 
    await collection.insert_many(contents_dict)
        
    return {"message": "Page scraped and inserted"}

@router.delete("/delete/single/{query_str}")
async def get_pages(query_str:str):
    query: Dict = json.loads(query_str)
    await collection.delete_one(query)
    return {"message": f"Query deleted successful: {query}"}

@router.delete("/delete/all/{query_str}")
async def get_pages(query_str:str):
    query: Dict = json.loads(query_str)
    await collection.delete_many(query)
    return {"message": f"Querys deleted successful: {query}"}