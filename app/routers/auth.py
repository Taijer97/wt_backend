from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.employee import Employee
from ..schemas.auth import LoginRequest, LoginResponse
from ..utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)):
    q = await session.execute(select(Employee).where(Employee.doc_number == payload.doc_number))
    emp = q.scalars().first()
    if not emp or not verify_password(payload.password, emp.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return LoginResponse(success=True, user_id=emp.id, role=emp.role, message="Login correcto")
