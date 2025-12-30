from pydantic import BaseModel


class IntermediaryCreate(BaseModel):
    name: str
    doc_number: str
    ruc_number: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class IntermediaryOut(BaseModel):
    id: int
    name: str
    doc_number: str
    ruc_number: str | None
    phone: str | None
    email: str | None
    address: str | None

    class Config:
        from_attributes = True


class IntermediaryUpdate(BaseModel):
    name: str | None = None
    ruc_number: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
