from fastapi import APIRouter
from ...db.database import client, db, collection
from contextlib import asynccontextmanager
from logging import info 
import logging
from ...parsing.scrape import Firecrawl
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
    
@router.get("/all")
async def get_pages():
    cursor = collection.find({})
    documents = []
    async for document in cursor:  # Use async for here
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        documents.append(document)
    return documents

@router.post("/page/{url}")
async def post_page(url:str):
    firecrawl = Firecrawl()
    result = firecrawl.get_structured_output(url)
    # Insert the structured result into MongoDB
    await collection.insert_one(result)
    return {"message": "Page scraped and inserted", "data": result}

@router.post("/pages/")
async def post_pages(urls:List[str]):
    pass

@router.put("/update/{id}")
async def get_pages(id: str):
    pass

@router.delete("/delete/pages/")
async def get_pages(ids:List[str]):
    pass

@router.delete("/delete/page/{id}")
async def get_pages(id: str):
    pass