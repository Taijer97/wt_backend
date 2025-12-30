import asyncio
import os
import sys
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine

async def check_schema():
    async with engine.connect() as conn:
        print("Checking 'employees' table schema...")
        result = await conn.execute(text("DESCRIBE employees"))
        columns = result.fetchall()
        for col in columns:
            print(col)

if __name__ == "__main__":
    asyncio.run(check_schema())
