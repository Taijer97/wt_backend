from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, JSON
from ..db.session import Base

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # e.g., "ADMIN", "USER"
    label: Mapped[str] = mapped_column(String(100))  # e.g., "Administrador del Sistema"
    permissions: Mapped[dict] = mapped_column(JSON)  # JSON structure of permissions
