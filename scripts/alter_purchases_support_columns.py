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
    "voucher_url": "ALTER TABLE purchases ADD COLUMN voucher_url VARCHAR(200) NULL",
    "contract_url": "ALTER TABLE purchases ADD COLUMN contract_url VARCHAR(200) NULL",
    "dj_url": "ALTER TABLE purchases ADD COLUMN dj_url VARCHAR(200) NULL",
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
    print("Purchases support columns verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
