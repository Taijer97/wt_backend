from pydantic import BaseModel


class ProductCreate(BaseModel):
    category: str
    serial_number: str | None = None
    brand: str | None = None
    model: str | None = None
    specs: str | None = None
    condition: str | None = None
    status: str = "IN_STOCK_RUC10"
    origin: str | None = None
    stock: int = 1
    purchase_price: float | None = None
    notary_cost: float | None = None
    total_cost: float | None = None
    intermediary_id: int | None = None
    
class ProductUpdate(BaseModel):
    category: str | None = None
    serial_number: str | None = None
    brand: str | None = None
    model: str | None = None
    specs: str | None = None
    condition: str | None = None
    status: str | None = None
    origin: str | None = None
    stock: int | None = None
    purchase_price: float | None = None
    notary_cost: float | None = None
    total_cost: float | None = None
    intermediary_id: int | None = None


class ProductOut(BaseModel):
    id: int
    category: str
    serial_number: str | None = None
    brand: str | None = None
    model: str | None = None
    specs: str | None = None
    condition: str | None = None
    status: str
    origin: str | None = None
    stock: int
    purchase_price: float | None = None
    notary_cost: float | None = None
    total_cost: float | None = None
    intermediary_id: int | None = None

    class Config:
        from_attributes = True
