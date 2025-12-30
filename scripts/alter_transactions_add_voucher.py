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
            "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'transactions'"
        )
        cols = {row[0] for row in result.fetchall()}
        if "voucher_url" not in cols:
            await conn.exec_driver_sql("ALTER TABLE transactions ADD COLUMN voucher_url VARCHAR(200) NULL")
            print("Added column: voucher_url")
        else:
            print("Column already exists: voucher_url")
    await engine.dispose()
    print("Transactions voucher_url column verification complete.")


if __name__ == "__main__":
    asyncio.run(run())
