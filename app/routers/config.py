from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db.session import get_session
from ..models.config import SystemConfig
from ..schemas.config import ConfigIn, ConfigOut
import json


router = APIRouter(prefix="/config", tags=["config"])


def map_out(c: SystemConfig) -> ConfigOut:
    return ConfigOut(
        companyName=c.company_name,
        companyRuc=c.company_ruc,
        companyAddress=c.company_address,
        companyDepartment=c.company_department,
        companyProvince=c.company_province,
        companyDistrict=c.company_district,
        companyPhone=c.company_phone,
        companyEmail=c.company_email,
        uit=c.uit,
        rmv=c.rmv,
        igvRate=c.igv_rate,
        rentaRate=c.renta_rate,
        defaultNotaryCost=c.default_notary_cost,
        ruc10Margin=c.ruc10_margin,
        ruc10MarginType=c.ruc10_margin_type,
        ruc20SaleMargin=c.ruc20_sale_margin,
        ruc20SaleMarginType=c.ruc20_sale_margin_type,
        isIgvExempt=c.is_igv_exempt,
        igvExemptionReason=c.igv_exemption_reason,
        ruc10TaxRegime=c.ruc10_tax_regime,
        ruc20TaxRegime=c.ruc20_tax_regime,
        ruc10DeclarationDay=c.ruc10_declaration_day,
        ruc20DeclarationDay=c.ruc20_declaration_day,
        productCategories=json.loads(c.product_categories or "[]"),
        roleConfigs=json.loads(c.role_configs or "[]"),
    )


@router.get("", response_model=ConfigOut)
async def get_config(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SystemConfig).limit(1))
    cfg = result.scalars().first()
    if not cfg:
        cfg = SystemConfig(id=1)
        session.add(cfg)
        await session.commit()
        await session.refresh(cfg)
    return map_out(cfg)


@router.put("", response_model=ConfigOut)
async def update_config(payload: ConfigIn, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(SystemConfig).limit(1))
    cfg = result.scalars().first()
    if not cfg:
        cfg = SystemConfig(id=1)
        session.add(cfg)
        await session.flush()
    cfg.company_name = payload.companyName
    cfg.company_ruc = payload.companyRuc
    cfg.company_address = payload.companyAddress
    cfg.company_department = payload.companyDepartment
    cfg.company_province = payload.companyProvince
    cfg.company_district = payload.companyDistrict
    cfg.company_phone = payload.companyPhone
    cfg.company_email = payload.companyEmail
    cfg.uit = payload.uit
    cfg.rmv = payload.rmv
    cfg.igv_rate = payload.igvRate
    cfg.renta_rate = payload.rentaRate
    cfg.default_notary_cost = payload.defaultNotaryCost
    cfg.ruc10_margin = payload.ruc10Margin
    cfg.ruc10_margin_type = payload.ruc10MarginType
    cfg.ruc20_sale_margin = payload.ruc20SaleMargin
    cfg.ruc20_sale_margin_type = payload.ruc20SaleMarginType
    cfg.is_igv_exempt = payload.isIgvExempt
    cfg.igv_exemption_reason = payload.igvExemptionReason
    cfg.ruc10_tax_regime = payload.ruc10TaxRegime
    cfg.ruc20_tax_regime = payload.ruc20TaxRegime
    cfg.ruc10_declaration_day = payload.ruc10DeclarationDay
    cfg.ruc20_declaration_day = payload.ruc20DeclarationDay
    cfg.product_categories = json.dumps(payload.productCategories or [])
    cfg.role_configs = json.dumps(payload.roleConfigs or [])
    await session.commit()
    await session.refresh(cfg)
    return map_out(cfg)
