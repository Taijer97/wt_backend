import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine

SCRIPT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

from app.core.config import settings


async def run():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS system_config (
            id INT PRIMARY KEY AUTO_INCREMENT,
            company_name VARCHAR(200) DEFAULT '',
            company_ruc VARCHAR(20) DEFAULT '',
            company_address VARCHAR(200) DEFAULT '',
            company_department VARCHAR(100) DEFAULT '',
            company_province VARCHAR(100) DEFAULT '',
            company_district VARCHAR(100) DEFAULT '',
            company_phone VARCHAR(50) DEFAULT '',
            company_email VARCHAR(100) DEFAULT '',
            uit DOUBLE DEFAULT 0,
            rmv DOUBLE DEFAULT 0,
            igv_rate DOUBLE DEFAULT 0.18,
            renta_rate DOUBLE DEFAULT 0,
            default_notary_cost DOUBLE DEFAULT 0,
            ruc10_margin DOUBLE DEFAULT 0,
            ruc10_margin_type VARCHAR(20) DEFAULT 'PERCENT',
            ruc20_sale_margin DOUBLE DEFAULT 0,
            ruc20_sale_margin_type VARCHAR(20) DEFAULT 'PERCENT',
            is_igv_exempt BOOLEAN DEFAULT 0,
            igv_exemption_reason VARCHAR(300) DEFAULT '',
            ruc10_tax_regime VARCHAR(30) DEFAULT 'REGIMEN_ESPECIAL',
            ruc20_tax_regime VARCHAR(30) DEFAULT 'REGIMEN_MYPE',
            ruc10_declaration_day INT DEFAULT 1,
            ruc20_declaration_day INT DEFAULT 1,
            product_categories TEXT,
            role_configs TEXT
        )
        """)
        # Seed a default row if table is empty
        result = await conn.exec_driver_sql("SELECT COUNT(*) FROM system_config")
        count = result.fetchone()[0]
        if count == 0:
            await conn.exec_driver_sql("INSERT INTO system_config (id, product_categories, role_configs) VALUES (1, '[]', '[]')")
            print("Seeded default system_config row")
    await engine.dispose()
    print("System config table ensured.")


if __name__ == "__main__":
    asyncio.run(run())
