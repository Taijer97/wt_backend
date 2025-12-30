from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
from ..db.session import Base
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trx_type: Mapped[str] = mapped_column(String(20))  # sale | purchase
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    document_type: Mapped[str] = mapped_column(String(20))
    document_number: Mapped[str] = mapped_column(String(50))
    entity_name: Mapped[str] = mapped_column(String(200))
    entity_doc_number: Mapped[str] = mapped_column(String(20))
    base_amount: Mapped[float] = mapped_column(Float, default=0)
    igv_amount: Mapped[float] = mapped_column(Float, default=0)
    total_amount: Mapped[float] = mapped_column(Float, default=0)
    sunat_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    voucher_url: Mapped[str | None] = mapped_column(String(200), nullable=True)

    items: Mapped[list["TransactionItem"]] = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan", lazy="selectin")


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    unit_price_base: Mapped[float] = mapped_column(Float, default=0)
    total_base: Mapped[float] = mapped_column(Float, default=0)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="items")
