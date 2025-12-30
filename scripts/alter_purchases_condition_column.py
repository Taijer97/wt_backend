import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

SCRIPT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from app.core.config import settings


async def run():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'purchases'"
        )
        cols = {row[0] for row in result.fetchall()}
        if "product_condition" not in cols:
            await conn.exec_driver_sql("ALTER TABLE purchases ADD COLUMN product_condition VARCHAR(20) NULL")
            print("Added column: product_condition")
        else:
            print("Column already exists: product_condition")
    await engine.dispose()
    print("Purchases condition column verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
