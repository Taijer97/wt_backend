from pydantic import BaseModel
from datetime import datetime


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    date: datetime | None = None
    status: str = "PENDING"

class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: float | None = None
    date: datetime | None = None
    status: str | None = None
    pdf_url: str | None = None


class ExpenseOut(BaseModel):
    id: int
    description: str
    amount: float
    date: datetime
    status: str
    pdf_url: str | None = None

    class Config:
        from_attributes = True
