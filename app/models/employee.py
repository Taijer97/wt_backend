from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey
from ..db.session import Base
from typing import Optional
from .role import Role


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(200))
    doc_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(String(200), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    base_salary: Mapped[int] = mapped_column(Integer, default=1130)
    pension_system: Mapped[str] = mapped_column(String(20), default="ONP")
    has_children: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(20), default="USER", index=True) # Legacy string column
    
    role_id: Mapped[int | None] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role_rel: Mapped["Role"] = relationship("Role", lazy="selectin")

