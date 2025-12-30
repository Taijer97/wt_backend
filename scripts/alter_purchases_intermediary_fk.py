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
        if "intermediary_id" not in cols:
            await conn.exec_driver_sql("ALTER TABLE purchases ADD COLUMN intermediary_id INT NULL")
            print("Added column: intermediary_id")
        else:
            print("Column already exists: intermediary_id")
    await engine.dispose()
    print("Purchases intermediary column verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
