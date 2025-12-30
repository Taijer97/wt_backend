import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

SCRIPT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from app.core.config import settings


DDL = {
    "ruc_number": "ALTER TABLE intermediaries ADD COLUMN ruc_number VARCHAR(20) NULL",
    "phone": "ALTER TABLE intermediaries ADD COLUMN phone VARCHAR(30) NULL",
    "email": "ALTER TABLE intermediaries ADD COLUMN email VARCHAR(100) NULL",
    "address": "ALTER TABLE intermediaries ADD COLUMN address VARCHAR(200) NULL",
}


async def run():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'intermediaries'"
        )
        cols = {row[0] for row in result.fetchall()}
        for col, stmt in DDL.items():
            if col not in cols:
                await conn.exec_driver_sql(stmt)
                print(f"Added column: {col}")
            else:
                print(f"Column already exists: {col}")
    await engine.dispose()
    print("Intermediaries table columns verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
