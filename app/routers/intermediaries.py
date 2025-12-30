from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.intermediary import Intermediary
from ..schemas.intermediary import IntermediaryCreate, IntermediaryOut, IntermediaryUpdate

router = APIRouter(prefix="/intermediaries", tags=["intermediaries"])


@router.get("", response_model=list[IntermediaryOut])
async def list_intermediaries(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Intermediary))
    return result.scalars().all()


@router.post("", response_model=IntermediaryOut)
async def create_intermediary(payload: IntermediaryCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(Intermediary).where(Intermediary.doc_number == payload.doc_number))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Intermediario ya existe")
    i = Intermediary(**payload.model_dump())
    session.add(i)
    await session.commit()
    await session.refresh(i)
    return i


@router.delete("/{intermediary_id}")
async def delete_intermediary(intermediary_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Intermediary).where(Intermediary.id == intermediary_id))
    i = result.scalars().first()
    if not i:
        return {"deleted": False}
    await session.delete(i)
    await session.commit()
    return {"deleted": True}


@router.put("/{intermediary_id}", response_model=IntermediaryOut)
async def update_intermediary(intermediary_id: int, payload: IntermediaryUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Intermediary).where(Intermediary.id == intermediary_id))
    i = result.scalars().first()
    if not i:
        raise HTTPException(status_code=404, detail="Intermediario no encontrado")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(i, k, v)
    await session.commit()
    await session.refresh(i)
    return i
