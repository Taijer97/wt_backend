from pydantic import BaseModel
from datetime import datetime


class PurchaseItemCreate(BaseModel):
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    serial: str | None = None
    specs: str | None = None
    cost: float | None = None

class PurchaseItemOut(BaseModel):
    id: int
    category: str | None
    brand: str | None
    model: str | None
    serial: str | None
    specs: str | None
    cost: float | None

    class Config:
        from_attributes = True

class PurchaseCreate(BaseModel):
    type: str = "RUC10"
    document_number: str
    date: datetime | None = None
    supplier_id: int | None = None
    intermediary_id: int | None = None
    seller_doc_number: str | None = None
    seller_full_name: str | None = None
    seller_address: str | None = None
    seller_civil_status: str | None = None
    status: str = "PENDING"
    base_amount: float = 0
    igv_amount: float = 0
    total_amount: float = 0
    pdf_url: str | None = None
    voucher_url: str | None = None
    contract_url: str | None = None
    dj_url: str | None = None
    provider_name: str | None = None
    product_brand: str | None = None
    product_model: str | None = None
    product_serial: str | None = None
    product_condition: str | None = None
    items: list[PurchaseItemCreate] = []

class PurchaseUpdate(BaseModel):
    type: str | None = None
    document_number: str | None = None
    date: datetime | None = None
    supplier_id: int | None = None
    intermediary_id: int | None = None
    status: str | None = None
    base_amount: float | None = None
    igv_amount: float | None = None
    total_amount: float | None = None
    pdf_url: str | None = None
    voucher_url: str | None = None
    contract_url: str | None = None
    dj_url: str | None = None
    provider_name: str | None = None
    product_brand: str | None = None
    product_model: str | None = None
    product_serial: str | None = None
    product_condition: str | None = None
    items: list[PurchaseItemCreate] | None = None


class PurchaseOut(BaseModel):
    id: int
    type: str
    document_number: str
    date: datetime
    supplier_id: int | None
    intermediary_id: int | None
    seller_id: int | None
    seller_doc_number: str | None
    seller_full_name: str | None
    seller_address: str | None
    seller_civil_status: str | None
    status: str
    base_amount: float
    igv_amount: float
    total_amount: float
    pdf_url: str | None
    voucher_url: str | None
    contract_url: str | None
    dj_url: str | None
    provider_name: str | None
    product_brand: str | None
    product_model: str | None
    product_serial: str | None
    product_condition: str | None
    items: list[PurchaseItemOut] = []
    # convenience fields for intermediary
    intermediary_name: str | None = None
    intermediary_doc_number: str | None = None
    intermediary_ruc_number: str | None = None
    intermediary_address: str | None = None

    class Config:
        from_attributes = True
