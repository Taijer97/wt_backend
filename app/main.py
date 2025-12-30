from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import health, employees, products, auth, ws, suppliers, intermediaries, expenses, purchases, transactions, config, roles


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://509ffb6e801a.ngrok-free.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(products.router)
app.include_router(ws.router)
app.include_router(suppliers.router)
app.include_router(intermediaries.router)
app.include_router(expenses.router)
app.include_router(purchases.router)
app.include_router(transactions.router)
app.include_router(config.router)
app.include_router(roles.router)

# Static files for uploaded documents (serve from app/uploads)
APP_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOADS_DIR = os.path.join(APP_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=UPLOADS_DIR), name="files")


@app.get("/")
async def root():
    return {"app": settings.app_name, "env": settings.app_env}
