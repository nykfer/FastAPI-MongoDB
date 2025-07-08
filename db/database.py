from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncMongoClient(os.getenv("MONGODB-CONNECTION-URI"))
db = client.clasiffication
collection = db["web_pages"]