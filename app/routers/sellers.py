from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.seller import Seller
from ..schemas.seller import SellerCreate, SellerOut, SellerUpdate

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("", response_model=list[SellerOut])
async def list_sellers(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Seller))
    return result.scalars().all()


@router.post("", response_model=SellerOut)
async def create_seller(payload: SellerCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(Seller).where(Seller.doc_number == payload.doc_number))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Vendedor ya existe")
    s = Seller(**payload.model_dump())
    session.add(s)
    await session.commit()
    await session.refresh(s)
    return s


@router.put("/{seller_id}", response_model=SellerOut)
async def update_seller(seller_id: int, payload: SellerUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    s = result.scalars().first()
    if not s:
        raise HTTPException(status_code=404, detail="Vendedor no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)
    await session.commit()
    await session.refresh(s)
    return s


@router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Seller).where(Seller.id == seller_id))
    s = result.scalars().first()
    if not s:
        return {"deleted": False}
    await session.delete(s)
    await session.commit()
    return {"deleted": True}
