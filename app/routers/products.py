from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductOut, ProductUpdate
from .ws import manager

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
async def list_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product))
    return result.scalars().all()


@router.post("", response_model=ProductOut)
async def create_product(payload: ProductCreate, session: AsyncSession = Depends(get_session)):
    if payload.serial_number:
        exists = await session.execute(select(Product).where(Product.serial_number == payload.serial_number))
        current = exists.scalars().first()
        if current:
            data = payload.model_dump(exclude_unset=True)
            for k, v in data.items():
                if v is not None:
                    setattr(current, k, v)
            await session.commit()
            await session.refresh(current)
            await manager.broadcast(f"product.updated:{current.id}")
            return current
    prod = Product(**payload.model_dump())
    session.add(prod)
    await session.commit()
    await session.refresh(prod)
    await manager.broadcast(f"product.created:{prod.id}")
    return prod


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, payload: ProductUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product).where(Product.id == product_id))
    prod = result.scalars().first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(prod, k, v)
    await session.commit()
    await session.refresh(prod)
    await manager.broadcast(f"product.updated:{prod.id}")
    return prod
