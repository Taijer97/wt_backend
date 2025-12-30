from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.expense import Expense
from ..schemas.expense import ExpenseCreate, ExpenseOut, ExpenseUpdate
from pathlib import Path
import os, time

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseOut])
async def list_expenses(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense))
    return result.scalars().all()


@router.post("", response_model=ExpenseOut)
async def create_expense(payload: ExpenseCreate, session: AsyncSession = Depends(get_session)):
    e = Expense(**payload.model_dump())
    session.add(e)
    await session.commit()
    await session.refresh(e)
    return e


@router.put("/{expense_id}", response_model=ExpenseOut)
async def update_expense(expense_id: int, payload: ExpenseUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense).where(Expense.id == expense_id))
    e = result.scalars().first()
    if not e:
        return e
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(e, k, v)
    await session.commit()
    await session.refresh(e)
    return e


@router.delete("/{expense_id}")
async def delete_expense(expense_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense).where(Expense.id == expense_id))
    e = result.scalars().first()
    if not e:
        return {"deleted": False}
    await session.delete(e)
    await session.commit()
    return {"deleted": True}


@router.post("/{expense_id}/upload")
async def upload_expense_file(expense_id: int, file: UploadFile = File(...), request: Request = None, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense).where(Expense.id == expense_id))
    e = result.scalars().first()
    if not e:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    ct = (file.content_type or "").lower()
    if not (ct.startswith("application/pdf") or ct.startswith("image/")):
        raise HTTPException(status_code=400, detail="Solo PDF o imágenes")
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "expenses"
    base_dir.mkdir(parents=True, exist_ok=True)
    def slug(s: str | None):
        if not s:
            return ""
        return "".join(ch.lower() if ch.isalnum() or ch in ("-", "_") else "-" for ch in s).strip("-")
    ts = time.strftime("%Y%m%d%H%M%S")
    ext = os.path.splitext(file.filename or "")[1].lower() or ".pdf"
    safe_name = f"expense-{slug(e.description)}-{ts}{ext}"
    dst = base_dir / safe_name
    data = await file.read()
    dst.write_bytes(data)
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/files/expenses/{safe_name}"
    e.pdf_url = url
    await session.commit()
    return {"url": url, "filename": safe_name}


@router.get("/{expense_id}/download")
async def download_expense_file(expense_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Expense).where(Expense.id == expense_id))
    e = result.scalars().first()
    if not e:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    if not e.pdf_url:
        raise HTTPException(status_code=404, detail="Sustento no disponible")
    fname = os.path.basename(e.pdf_url)
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "expenses"
    file_path = base_dir / fname
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(path=str(file_path), filename=fname)
