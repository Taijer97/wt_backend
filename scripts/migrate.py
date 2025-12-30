import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

SCRIPT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from app.db.session import Base
from app.core.config import settings
import app.db.base


async def run():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("Migración completada.")


if __name__ == "__main__":
    asyncio.run(run())
