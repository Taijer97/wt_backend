import asyncio
import httpx


async def main():
    base = "http://localhost:8000"
    payload = {
        "full_name": "Admin General",
        "doc_number": "70871370",
        "password": "123456",
        "base_salary": 3000,
        "pension_system": "ONP",
        "has_children": False,
        "role": "ADMIN",
    }
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            r = await client.post(f"{base}/employees", json=payload)
            print("POST /employees:", r.status_code, r.text)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
