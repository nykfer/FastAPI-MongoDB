from fastapi import APIRouter, HTTPException, status
from ...db.database import client, db, collection
from contextlib import asynccontextmanager
from logging import info 
import logging
import json
from typing import List

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

@router.get("/one/")
async def get_page(id:str):
    pass
    
@router.get("/all", status_code=status.HTTP_200_OK)
async def get_pages():
    
    cursor = collection.find({})
    documents = []
    async for document in cursor:  # Use async for here
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        documents.append(document)
    
    if documents == []:
        raise HTTPException(status_code=204, detail="DataBase has not any data")
    else: return documents

@router.post("/content/{content}", status_code=status.HTTP_201_CREATED)
async def post_page(url:str, content: dict):
    # Insert the structured result into MongoDB
    await collection.insert_one(content)
    return {"message": "Content and inserted"}

@router.post("/contents/{contents}")
async def post_pages(contents:List[dict], skip_error:bool):
    contents_len = len(contents)
    
    async for index in urls_len:
        if ("error" in urls[index]) and (skip_error == True): continue
        
        result = {"url": urls[index]}
        result += contents[index]
        await collection.insert_one(result)
        
    return {"message": "Page scraped and inserted", "urls": urls}

@router.put("/update/{id}")
async def get_pages(id: str):
    pass

@router.delete("/delete/pages/")
async def get_pages(ids:List[str]):
    pass

@router.delete("/delete/page/{id}")
async def get_pages(id: str):
    pass