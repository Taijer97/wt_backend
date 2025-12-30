from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    ruc: str
    contact: str | None = None
    category: str | None = None
    department: str | None = None
    province: str | None = None
    district: str | None = None
    address: str | None = None
    phone: str | None = None


class SupplierOut(BaseModel):
    id: int
    name: str
    ruc: str
    contact: str | None = None
    category: str | None = None
    department: str | None = None
    province: str | None = None
    district: str | None = None
    address: str | None = None
    phone: str | None = None

    class Config:
        from_attributes = True


class SupplierUpdate(BaseModel):
    name: str | None = None
    contact: str | None = None
    category: str | None = None
    department: str | None = None
    province: str | None = None
    district: str | None = None
    address: str | None = None
    phone: str | None = None
