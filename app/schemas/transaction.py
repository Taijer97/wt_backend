from pydantic import BaseModel
from datetime import datetime


class TransactionItemCreate(BaseModel):
    product_id: int | None = None
    product_name: str
    quantity: int = 1
    unit_price_base: float = 0
    total_base: float = 0


class TransactionCreate(BaseModel):
    trx_type: str
    document_type: str
    document_number: str
    entity_name: str
    entity_doc_number: str
    base_amount: float = 0
    igv_amount: float = 0
    total_amount: float = 0
    sunat_status: str | None = None
    pdf_url: str | None = None
    items: list[TransactionItemCreate] = []

class TransactionItemOut(BaseModel):
    product_id: int | None = None
    product_name: str
    quantity: int
    unit_price_base: float
    total_base: float

    class Config:
        from_attributes = True

class TransactionOut(BaseModel):
    id: int
    trx_type: str
    date: datetime | None = None
    document_type: str
    document_number: str
    entity_name: str
    entity_doc_number: str
    base_amount: float
    igv_amount: float
    total_amount: float
    sunat_status: str | None
    pdf_url: str | None
    voucher_url: str | None
    items: list[TransactionItemOut] = []

    class Config:
        from_attributes = True
