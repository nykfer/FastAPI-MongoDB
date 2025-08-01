# 🧠 ML Pet Project – Article Classification by Science Fields

This project is a machine learning-based application that classifies academic articles into various science fields. It uses **FastAPI** as the web framework and **MongoDB Atlas** for database storage.

---

## 📁 Project Structure

- `db/database.py` – MongoDB connection logic  
- `main.py` – FastAPI application setup using lifespan events  
- `models/`, `routes/`, etc. – ML model logic, API endpoints, etc. *(assumed standard layout)*

---

## 🌐 MongoDB Atlas Integration

### What is MongoDB Atlas?

MongoDB Atlas is a fully managed cloud database service.  
📖 Learn more: [MongoDB Atlas Structure – Perplexity.ai](https://www.perplexity.ai/search/what-is-the-structure-of-mogng-Hwz.KmnnSnuwrxcXm.ttTw)

---

## ⚙️ Async Connection to MongoDB

This project uses **PyMongo's async API** because **Motor** will be deprecated on **May 14, 2026**.

📖 Official guide: [Migrate to PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/)

> **Note**: The database and collection are automatically created upon inserting the first document.  
> Implementation is located in: `db/database.py`

---

## ✅ Checking MongoDB Connection with FastAPI Lifespan Events

To ensure that MongoDB is connected before serving any requests, the app uses **FastAPI's lifespan events**.

### 🔄 How It Works

1. On **startup**:
   - Connect to MongoDB
   - Send a `ping` command
   - Log success if connection is OK

2. On **shutdown**:
   - Gracefully close the MongoDB client

### 🧩 Example Code

```python
from ..db.database import client, db
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
