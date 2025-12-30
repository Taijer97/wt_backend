import asyncio
import os
from pathlib import Path
import httpx


async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post("http://localhost:8000/purchases", json={
            "type": "RUC10",
            "document_number": "SN-DEL-TEST",
            "base_amount": 100,
            "igv_amount": 0,
            "total_amount": 120,
            "provider_name": "Juan Perez",
            "product_brand": "Lenovo",
            "product_model": "Ideapad",
            "product_serial": "SN-DEL-TEST",
        })
        created = r.json()
        pid = created["id"]
        files = {
            "voucher": ("voucher.pdf", b"%PDF voucher", "application/pdf"),
            "contract": ("contrato.pdf", b"%PDF contrato", "application/pdf"),
            "dj": ("dj.pdf", b"%PDF dj", "application/pdf"),
        }
        for kind, ftuple in files.items():
            r2 = await client.post(f"http://localhost:8000/purchases/{pid}/upload", files={"file": ftuple}, data={"doc_kind": kind})
            print("Uploaded", kind, r2.json())
        base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
        names = [n for n in os.listdir(base_dir) if f"ruc10-{pid}" in n]
        print("Files before delete:", names)
        rd = await client.delete(f"http://localhost:8000/purchases/{pid}")
        print("Delete response:", rd.json())
        names_after = [n for n in os.listdir(base_dir) if f"ruc10-{pid}" in n]
        print("Files after delete:", names_after)


if __name__ == "__main__":
    asyncio.run(main())
