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
        # Create sellers table if not exists
        await conn.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS sellers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doc_number VARCHAR(20) UNIQUE,
                full_name VARCHAR(200) NOT NULL,
                address VARCHAR(200) NULL,
                civil_status VARCHAR(20) NULL,
                phone VARCHAR(30) NULL,
                email VARCHAR(100) NULL
            )
        """)
        # Add seller_id column to purchases if missing
        result = await conn.exec_driver_sql(
            "SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'purchases'"
        )
        cols = {row[0] for row in result.fetchall()}
        if "seller_id" not in cols:
            await conn.exec_driver_sql("ALTER TABLE purchases ADD COLUMN seller_id INT NULL")
        print("Sellers table ensured and purchases.seller_id column verified.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
