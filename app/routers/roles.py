from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.role import Role
from ..schemas.role import RoleCreate, RoleUpdate, RoleOut

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("", response_model=list[RoleOut])
async def list_roles(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Role))
    return result.scalars().all()

@router.post("", response_model=RoleOut)
async def create_role(payload: RoleCreate, session: AsyncSession = Depends(get_session)):
    # Check if name exists
    exists = await session.execute(select(Role).where(Role.name == payload.name))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    role = Role(
        name=payload.name,
        label=payload.label,
        permissions=payload.permissions
    )
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role

@router.put("/{role_id}", response_model=RoleOut)
async def update_role(role_id: int, payload: RoleUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if payload.name:
        # Check uniqueness if name changing
        if payload.name != role.name:
            exists = await session.execute(select(Role).where(Role.name == payload.name))
            if exists.scalars().first():
                raise HTTPException(status_code=400, detail="Role name already exists")
        role.name = payload.name
        
    if payload.label:
        role.label = payload.label
    if payload.permissions:
        role.permissions = payload.permissions
        
    await session.commit()
    await session.refresh(role)
    return role

@router.delete("/{role_id}")
async def delete_role(role_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.name == "ADMIN":
        raise HTTPException(status_code=400, detail="Cannot delete ADMIN role")
        
    await session.delete(role)
    await session.commit()
    return {"message": "Role deleted"}
