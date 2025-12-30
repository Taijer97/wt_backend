from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from ..db.session import Base
from datetime import datetime


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), default="RUC10")
    document_number: Mapped[str] = mapped_column(String(50), index=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    seller_id: Mapped[int | None] = mapped_column(ForeignKey("sellers.id"), nullable=True)
    intermediary_id: Mapped[int | None] = mapped_column(ForeignKey("intermediaries.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    base_amount: Mapped[float] = mapped_column(Float, default=0)
    igv_amount: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    pdf_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    voucher_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contract_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    dj_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    product_brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_serial: Mapped[str | None] = mapped_column(String(100), nullable=True)
    product_condition: Mapped[str | None] = mapped_column(String(20), nullable=True)

    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
