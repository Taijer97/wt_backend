import asyncio
import os
import sys
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine

async def add_role_column():
    async with engine.begin() as conn:
        print("Adding 'role' column back to employees table...")
        # Add role column as string, nullable first, default 'USER'
        await conn.execute(text("ALTER TABLE employees ADD COLUMN role VARCHAR(20) DEFAULT 'USER'"))
        # Update existing records to match role_id if possible, or just default to USER
        # We can try to sync from roles table if we want, but for now 'USER' is safe
        # Or even better:
        await conn.execute(text("UPDATE employees SET role = 'ADMIN' WHERE role_id = 1"))
        await conn.execute(text("UPDATE employees SET role = 'USER' WHERE role_id = 2"))
        
    print("Column added.")

if __name__ == "__main__":
    asyncio.run(add_role_column())
