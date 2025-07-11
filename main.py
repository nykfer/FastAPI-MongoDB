from db.database import client, db, collection
from parsing.scrape import Firecrawl
import asyncio
from urls import pages

firecrawl = Firecrawl()

async def send_pages():
        for url in pages:
            result = firecrawl.get_structured_output(url)
            await collection.insert_one(result)

if __name__ == "__main__":
    asyncio.run(send_pages())