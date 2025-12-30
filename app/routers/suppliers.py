from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.supplier import Supplier
from ..schemas.supplier import SupplierCreate, SupplierOut, SupplierUpdate

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=list[SupplierOut])
async def list_suppliers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Supplier))
    return result.scalars().all()


@router.post("", response_model=SupplierOut)
async def create_supplier(payload: SupplierCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(Supplier).where(Supplier.ruc == payload.ruc))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Proveedor ya existe")
    s = Supplier(**payload.model_dump())
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Supplier).where(Supplier.id == supplier_id))
    s = result.scalars().first()
    if not s:
        return {"deleted": False}
    await session.delete(s)
    await session.commit()
    return {"deleted": True}


@router.put("/{supplier_id}", response_model=SupplierOut)
async def update_supplier(supplier_id: int, payload: SupplierUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Supplier).where(Supplier.id == supplier_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)
    await session.commit()
    await session.refresh(s)
    return s
