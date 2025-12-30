from pydantic import BaseModel, EmailStr


class SellerCreate(BaseModel):
    doc_number: str
    full_name: str
    address: str | None = None
    civil_status: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class SellerUpdate(BaseModel):
    full_name: str | None = None
    address: str | None = None
    civil_status: str | None = None
    phone: str | None = None
    email: EmailStr | None = None


class SellerOut(BaseModel):
    id: int
    doc_number: str
    full_name: str
    address: str | None
    civil_status: str | None
    phone: str | None
    email: EmailStr | None

    class Config:
        from_attributes = True
