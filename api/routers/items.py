from fastapi import APIRouter, HTTPException, status, Query, Path, Body
from ...db.database import client, db, collection
from contextlib import asynccontextmanager
from logging import info 
import logging
import json
from typing import Annotated, Dict, List

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
async def get_page(query_str:Annotated[str, Path(max_length=3000,
                                                  min_length=7,
                                                  title="Query JSON",
                                                  description="""Query parameter for searching
                                                  in MongoDB DataBase""")]):
    
    try:
        query: Dict = json.loads(query_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid data input",
                            headers={"X-Error": "InvalidJSON"})
        
    document = await collection.find_one(query)
    
    if document is None:
        raise HTTPException(status_code=204,
                            detail="data not found",
                            headers={"X-Error": "Query doesn't match any data in the db"})
    document["_id"] = str(document["_id"])
    
    return document
    
@router.get("/find/all/", status_code=status.HTTP_200_OK)
async def get_pages(amount:Annotated[int, Query(title="Amount",
                                                       description="""Amount of results to return.
                                                       None means to return all""")] = 0,
                    query_str:Annotated[str, Query(max_length=3000,
                                                   min_length=7,
                                                  title="Query JSON",
                                                  description="""Query parameter for searching
                                                  in MongoDB DataBase. By
                                                   putting the default value, get  all
                                                   documents in the collection""")] = "{}"):
    
    try:
        query: Dict = json.loads(query_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid data input",
                            headers={"X-Error": "InvalidJSON"})
        
    cursor = collection.find(query, batch_size=amount)
    documents = []
    async for document in cursor:  # Use async for here
        document["_id"] = str(document["_id"])  # Convert ObjectId to string
        documents.append(document)
    
    if documents == []:
        raise HTTPException(status_code=204, detail="DataBase has not any data")
    else: return documents

@router.post("/content/{content_str}", status_code=status.HTTP_201_CREATED)
async def post_page(content_str: Annotated[str, Path(max_length=30000,
                                                      min_length=7,
                                                  title="Document JSON",
                                                  description="""Document to insert 
                                                  the MongoDB DataBase""")]):
    
    try:
        content: Dict = json.loads(content_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid data input",
                            headers={"X-Error": "InvalidJSON"})
        
    # Insert the structured result into MongoDB
    await collection.insert_one(content)
    return {"message": "Content and inserted"}

@router.post("/contents/", status_code=status.HTTP_201_CREATED)
async def post_pages(contents_str:Annotated[str, Body(..., media_type="text/plain",
                                                      title="Documents JSON",
                                                        description="""List of documents
                                                        to inseart to 
                                                        the MongoDB DataBase separeted by \n""")], 
                    skip_error:Annotated[bool, Query(description="""Define a flag to skip
                                                     collections with error message
                                                     or not. By default, not skipping""")] = False):    
    
    contents_dict: List[Dict] = []
    splitted_contents = contents_str.strip().split('\n')
    for content in splitted_contents:
        if ("error" in content) and (skip_error == True): 
            continue
        else:
            try:
                data: Dict = json.loads(content)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400,
                                    detail="Invalid data input",
                                    headers={"X-Error": f"InvalidJSON: {content}"})
            contents_dict.append(data)
    if contents_dict == []:
        raise HTTPException(status_code=204, detail="Has not any data to insert into db") 
    else: 
        await collection.insert_many(contents_dict)
        return {"message": "Page scraped and inserted"}

@router.delete("/delete/one/{query_str}")
async def get_pages(query_str:Annotated[str, Path(max_length=30000,
                                                      min_length=7,
                                                  title="Query JSON",
                                                  description="""Delete the first match 
                                                  with the query""")]):
    
    try:
        query: Dict = json.loads(query_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid data input",
                            headers={"X-Error": "InvalidJSON"})
        
    result = await collection.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=204, detail="The query doesn't match  any data")
    else: return {"message": f"Document deleted successful"}

@router.delete("/delete/all/{query_str}")
async def get_pages(query_str:Annotated[str, Path(max_length=30000,
                                                      min_length=7,
                                                  title="Query JSON",
                                                  description="""Query that matches the document
                                                  to delete""")]):
    
    try:
        query: Dict = json.loads(query_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400,
                            detail="Invalid data input",
                            headers={"X-Error": "InvalidJSON"})
        
    result = await collection.delete_many(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=204, detail="The query doesn't match  any data")
    else: return {"message": f"Documents deleted successful (amount:{result.deleted_count})"}