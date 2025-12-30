from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db.session import get_session
from ..models.transaction import Transaction, TransactionItem
from ..models.product import Product
from ..schemas.transaction import TransactionCreate, TransactionOut
from .ws import manager
from pathlib import Path
import os, time
from .ws import manager

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
async def list_transactions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Transaction).options(selectinload(Transaction.items)))
    return result.scalars().all()


@router.post("", response_model=TransactionOut)
async def create_transaction(payload: TransactionCreate, session: AsyncSession = Depends(get_session)):
    t = Transaction(
        trx_type=payload.trx_type,
        document_type=payload.document_type,
        document_number=payload.document_number,
        entity_name=payload.entity_name,
        entity_doc_number=payload.entity_doc_number,
        base_amount=payload.base_amount,
        igv_amount=payload.igv_amount,
        total_amount=payload.total_amount,
        sunat_status=payload.sunat_status,
        pdf_url=payload.pdf_url,
    )
    session.add(t)
    await session.flush()
    for item in payload.items:
        session.add(
            TransactionItem(
                transaction_id=t.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price_base=item.unit_price_base,
                total_base=item.total_base,
            )
        )
        if payload.trx_type == "sale" and item.product_id:
            prod = await session.get(Product, item.product_id)
            if prod:
                prod.stock = max(0, (prod.stock or 0) - item.quantity)
                if prod.stock == 0:
                    prod.status = "SOLD"
                session.add(prod)
    await session.commit()
    # Re-load with eager items to avoid async lazy-load during response serialization
    result = await session.execute(select(Transaction).options(selectinload(Transaction.items)).where(Transaction.id == t.id))
    t_loaded = result.scalars().first()
    await manager.broadcast(f"transaction.created:{t.id}")
    return t_loaded


@router.post("/{transaction_id}/upload")
async def upload_transaction_file(transaction_id: int, file: UploadFile = File(...), doc_kind: str = "invoice", request: Request = None, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    content_type = (file.content_type or "").lower()
    if not (content_type.startswith("application/pdf") or content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Solo se aceptan PDF o imágenes")
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "transactions"
    base_dir.mkdir(parents=True, exist_ok=True)
    def slug(s: str | None):
        if not s:
            return ""
        return "".join(ch.lower() if ch.isalnum() or ch in ("-", "_") else "-" for ch in s).strip("-")
    ts = time.strftime("%Y%m%d%H%M%S")
    ext = os.path.splitext(file.filename or "")[1].lower() or ".pdf"
    kind = doc_kind.lower()
    if kind not in ("invoice", "voucher", "other"):
        kind = "other"
    safe_name = f"{kind}-{slug(t.document_type)}-{slug(t.document_number)}-{ts}{ext}"
    dst = base_dir / safe_name
    data = await file.read()
    dst.write_bytes(data)
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/files/transactions/{safe_name}"
    if kind == "invoice":
        t.pdf_url = url
    elif kind == "voucher":
        t.voucher_url = url
    else:
        t.pdf_url = url
    await session.commit()
    return {"url": url, "filename": safe_name, "doc_kind": kind}


@router.get("/{transaction_id}/download/{doc_kind}")
async def download_transaction_file(transaction_id: int, doc_kind: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Transaction).where(Transaction.id == transaction_id))
    t = result.scalars().first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    kind = doc_kind.lower()
    url = None
    if kind == "invoice":
        url = t.pdf_url
    elif kind == "voucher":
        url = t.voucher_url
    else:
        url = t.pdf_url
    if not url:
        raise HTTPException(status_code=404, detail="Sustento no disponible")
    fname = os.path.basename(url)
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "transactions"
    file_path = base_dir / fname
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(path=str(file_path), filename=fname)
