from pydantic import BaseModel


class ConfigIn(BaseModel):
    companyName: str
    companyRuc: str
    companyAddress: str
    companyDepartment: str
    companyProvince: str
    companyDistrict: str
    companyPhone: str
    companyEmail: str
    uit: float
    rmv: float
    igvRate: float
    rentaRate: float
    defaultNotaryCost: float
    ruc10Margin: float
    ruc10MarginType: str
    ruc20SaleMargin: float
    ruc20SaleMarginType: str
    isIgvExempt: bool
    igvExemptionReason: str
    ruc10TaxRegime: str
    ruc20TaxRegime: str
    ruc10DeclarationDay: int
    ruc20DeclarationDay: int
    productCategories: list[str]
    roleConfigs: list


class ConfigOut(BaseModel):
    companyName: str
    companyRuc: str
    companyAddress: str
    companyDepartment: str
    companyProvince: str
    companyDistrict: str
    companyPhone: str
    companyEmail: str
    uit: float
    rmv: float
    igvRate: float
    rentaRate: float
    defaultNotaryCost: float
    ruc10Margin: float
    ruc10MarginType: str
    ruc20SaleMargin: float
    ruc20SaleMarginType: str
    isIgvExempt: bool
    igvExemptionReason: str
    ruc10TaxRegime: str
    ruc20TaxRegime: str
    ruc10DeclarationDay: int
    ruc20DeclarationDay: int
    productCategories: list[str]
    roleConfigs: list
