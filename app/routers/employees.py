from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.employee import Employee
from ..models.role import Role
from ..schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from ..utils.security import hash_password

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
async def list_employees(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee))
    return result.scalars().all()

@router.get("/{emp_id}", response_model=EmployeeOut)
async def get_employee(emp_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return emp

@router.post("", response_model=EmployeeOut)
async def create_employee(payload: EmployeeCreate, session: AsyncSession = Depends(get_session)):
    exists = await session.execute(select(Employee).where(Employee.doc_number == payload.doc_number))
    if exists.scalars().first():
        raise HTTPException(status_code=400, detail="Empleado ya existe")
    try:
        pwd_hash = hash_password(payload.password)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    
    # Resolve role_id from payload.role (string)
    role_res = await session.execute(select(Role).where(Role.name == payload.role))
    role_obj = role_res.scalars().first()
    role_id = role_obj.id if role_obj else None

    emp = Employee(
        full_name=payload.full_name,
        doc_number=payload.doc_number,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        password_hash=pwd_hash,
        base_salary=payload.base_salary,
        pension_system=payload.pension_system,
        has_children=payload.has_children,
        role=payload.role,
        role_id=role_id
    )
    session.add(emp)
    await session.commit()
    await session.refresh(emp)
    return emp


@router.put("/{emp_id}", response_model=EmployeeOut)
async def update_employee(emp_id: int, payload: EmployeeUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    data = payload.model_dump(exclude_unset=True)
    
    # If role is updated, sync role_id
    if 'role' in data:
        role_res = await session.execute(select(Role).where(Role.name == data['role']))
        role_obj = role_res.scalars().first()
        emp.role_id = role_obj.id if role_obj else None

    for k, v in data.items():
        setattr(emp, k, v)
    await session.commit()
    await session.refresh(emp)
    return emp


@router.delete("/{emp_id}")
async def delete_employee(emp_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Employee).where(Employee.id == emp_id))
    emp = result.scalars().first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    await session.delete(emp)
    await session.commit()
    return {"message": "Empleado eliminado correctamente"}
