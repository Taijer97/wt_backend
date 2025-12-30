import asyncio
import httpx


async def main():
    payload = {
        "type": "RUC20",
        "document_number": "F001-00000123",
        "base_amount": 1000,
        "igv_amount": 180,
        "total_amount": 1180,
        "provider_name": "Proveedor Mayorista",
        "items": [
            {"category": "Laptop", "brand": "DELL", "model": "VOSTRO", "serial": "SN-ABC", "specs": "i5 16GB", "cost": 1000}
        ],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post("http://localhost:8000/purchases", json=payload)
        print("CREATE:", r.status_code, r.text)
        r = await client.get("http://localhost:8000/purchases", params={"type": "RUC20", "limit": 10})
        print("LIST:", r.status_code, r.text)


if __name__ == "__main__":
    asyncio.run(main())
