from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, ForeignKey
from ..db.session import Base


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    serial: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    specs: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    purchase = relationship("Purchase", back_populates="items")
