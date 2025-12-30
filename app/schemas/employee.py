from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .role import RoleOut

class EmployeeCreate(BaseModel):
    full_name: str
    doc_number: str
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    password: str = Field(..., min_length=6, max_length=72)
    base_salary: int = 1130
    pension_system: str = "ONP"
    has_children: bool = False
    role: str = "USER"


class EmployeeOut(BaseModel):
    id: int
    full_name: str
    doc_number: str
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    base_salary: int
    pension_system: str
    has_children: bool
    role: str
    role_detail: Optional[RoleOut] = Field(default=None, alias="role_rel")

    class Config:
        from_attributes = True


class EmployeeUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    base_salary: int | None = None
    pension_system: str | None = None
    has_children: bool | None = None
    role: str | None = None
