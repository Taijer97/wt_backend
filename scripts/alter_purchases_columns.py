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
    "provider_name": "ALTER TABLE purchases ADD COLUMN provider_name VARCHAR(200) NULL",
    "product_brand": "ALTER TABLE purchases ADD COLUMN product_brand VARCHAR(100) NULL",
    "product_model": "ALTER TABLE purchases ADD COLUMN product_model VARCHAR(100) NULL",
    "product_serial": "ALTER TABLE purchases ADD COLUMN product_serial VARCHAR(100) NULL",
}


async def run():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'purchases'"
        )
        cols = {row[0] for row in result.fetchall()}
        for col, stmt in DDL.items():
            if col not in cols:
                await conn.exec_driver_sql(stmt)
                print(f"Added column: {col}")
            else:
                print(f"Column already exists: {col}")
    await engine.dispose()
    print("Purchases table columns verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
