import asyncio
import os
import sys
import httpx


async def main():
    base = "http://localhost:8000"
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"{base}/health")
        print("GET /health:", r.status_code, r.json())


if __name__ == "__main__":
    asyncio.run(main())
