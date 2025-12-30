from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from ..db.session import Base


class Intermediary(Base):
    __tablename__ = "intermediaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    doc_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    ruc_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
