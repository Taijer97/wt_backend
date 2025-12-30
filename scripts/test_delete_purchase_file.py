import asyncio
import os
from pathlib import Path
import httpx


async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post("http://localhost:8000/purchases", json={
            "type": "RUC20",
            "document_number": "F001-TEST-DEL",
            "base_amount": 10,
            "igv_amount": 1.8,
            "total_amount": 11.8,
            "provider_name": "Prov Test",
        })
        created = r.json()
        pid = created["id"]
        files = {"file": ("factura.pdf", b"%PDF-1.4 test content", "application/pdf")}
        r2 = await client.post(f"http://localhost:8000/purchases/{pid}/upload", files=files)
        url = r2.json()["url"]
        fname = os.path.basename(url)
        base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
        path = base_dir / fname
        print("File exists before delete:", path.exists(), str(path))
        r3 = await client.delete(f"http://localhost:8000/purchases/{pid}")
        print("Delete response:", r3.json())
        print("File exists after delete:", path.exists())


if __name__ == "__main__":
    asyncio.run(main())
