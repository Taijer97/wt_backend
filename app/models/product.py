from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, ForeignKey
from ..db.session import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50))
    serial_number: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    specs: Mapped[str | None] = mapped_column(String(200), nullable=True)
    condition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="IN_STOCK_RUC10", index=True)
    origin: Mapped[str | None] = mapped_column(String(60), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=1)
    purchase_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    notary_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    intermediary_id: Mapped[int | None] = mapped_column(ForeignKey("intermediaries.id"), nullable=True)
