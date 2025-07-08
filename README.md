# ML pet-project
### Clasiffication articles by science fields
#### Connect to the MongoDB Atlas
To get a brief understanding about mongodb atlas structure, follow the link below:
https://www.perplexity.ai/search/what-is-the-structure-of-mogng-Hwz.KmnnSnuwrxcXm.ttTw
For async connection with Atlas I use pymongo because Motor will be deprecated on May 14th, 2026. Read more you can here: 
Migrate to PyMongo Async: https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/
How to connect it, you can see in the db/database.py file. Database and collection will be created after inserting the first ellement into this collection
#### checking connection to the mongodb atlas
To check that database is connected successful, I use fastapi's lifespan events.Lifespan events are used to define logic (code) that should be executed before the application starts up and logic (code) that should be executed when the application is shutting down. In this case, this code will be executed once, before/after having handled possibly many requests. So, before fastapi's app starts its work we connect to the mongodb atlas, check its connection, and, if all is okay, app strarts work. After all is done we close connetction with the server. To do it you can by using this code:

from ..db.database import client, db, collection
from fastapi import FastAPI
from contextlib import asynccontextmanager
from logging import info 
import logging

logging.basicConfig(level=logging.INFO) # needed to see message from info() in the terminal

@asynccontextmanager
async def db_lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = client
    app.database = db
    ping_response = await app.database.command("ping") # a ping command is sent to the database to confirm it's reachable. If ping is successful (returns { "ok": 1.0 }), it logs
    if int(ping_response["ok"]) != 1:
        raise Exception("Problem connecting to database cluster.")
    else:
        info("Connected to database cluster.")
    
    yield
    # Shutdown
    await app.mongodb_client.close()

app: FastAPI = FastAPI(lifespan=db_lifespan)

References:
fastapi's lifespan events: https://fastapi.tiangolo.com/advanced/events/
8 Best Practices for Building FastAPI and MongoDB Applications: https://www.mongodb.com/developer/products/mongodb/8-fastapi-mongodb-best-practices/