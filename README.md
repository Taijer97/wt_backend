Backend FastAPI (WasiTech)

- Arranque: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- Variables `.env`: `DATABASE_URL`, `API_HOST`, `API_PORT`, `JWT_*`
- Requisitos: `pip install -r backend/requirements.txt`
- Migraciones: `python backend/scripts/migrate.py`
- Endpoints:
  - `GET /health`
  - `POST /auth/login`
  - `GET /employees`, `POST /employees`
  - `GET /products`, `POST /products`
  - WS: `ws://localhost:8000/ws/updates`
