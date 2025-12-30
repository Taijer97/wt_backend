from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, Boolean, Text
from ..db.session import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Empresa
    company_name: Mapped[str] = mapped_column(String(200), default="")
    company_ruc: Mapped[str] = mapped_column(String(20), default="")
    company_address: Mapped[str] = mapped_column(String(200), default="")
    company_department: Mapped[str] = mapped_column(String(100), default="")
    company_province: Mapped[str] = mapped_column(String(100), default="")
    company_district: Mapped[str] = mapped_column(String(100), default="")
    company_phone: Mapped[str] = mapped_column(String(50), default="")
    company_email: Mapped[str] = mapped_column(String(100), default="")
    # Variables
    uit: Mapped[float] = mapped_column(Float, default=0.0)
    rmv: Mapped[float] = mapped_column(Float, default=0.0)
    igv_rate: Mapped[float] = mapped_column(Float, default=0.18)
    renta_rate: Mapped[float] = mapped_column(Float, default=0.0)
    default_notary_cost: Mapped[float] = mapped_column(Float, default=0.0)
    # Márgenes
    ruc10_margin: Mapped[float] = mapped_column(Float, default=0.0)
    ruc10_margin_type: Mapped[str] = mapped_column(String(20), default="PERCENT")
    ruc20_sale_margin: Mapped[float] = mapped_column(Float, default=0.0)
    ruc20_sale_margin_type: Mapped[str] = mapped_column(String(20), default="PERCENT")
    # IGV
    is_igv_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    igv_exemption_reason: Mapped[str] = mapped_column(String(300), default="")
    # Regímenes
    ruc10_tax_regime: Mapped[str] = mapped_column(String(30), default="REGIMEN_ESPECIAL")
    ruc20_tax_regime: Mapped[str] = mapped_column(String(30), default="REGIMEN_MYPE")
    ruc10_declaration_day: Mapped[int] = mapped_column(Integer, default=1)
    ruc20_declaration_day: Mapped[int] = mapped_column(Integer, default=1)
    # Arrays/JSON
    product_categories: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    role_configs: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
