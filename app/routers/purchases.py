from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import FileResponse
from pathlib import Path
import os, time
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from ..db.session import get_session
from ..models.purchase import Purchase
from ..models.purchase_item import PurchaseItem
from ..schemas.purchase import PurchaseCreate, PurchaseOut, PurchaseUpdate
from ..models.seller import Seller
from ..models.intermediary import Intermediary

router = APIRouter(prefix="/purchases", tags=["purchases"])

async def _map_purchase_out(p: Purchase, session: AsyncSession):
    seller = None
    if getattr(p, "seller_id", None):
        sres = await session.execute(select(Seller).where(Seller.id == p.seller_id))
        seller = sres.scalars().first()
    intermediary = None
    if getattr(p, "intermediary_id", None):
        ires = await session.execute(select(Intermediary).where(Intermediary.id == p.intermediary_id))
        intermediary = ires.scalars().first()
    return {
        "id": p.id,
        "type": p.type,
        "document_number": p.document_number,
        "date": p.date,
        "supplier_id": p.supplier_id,
        "status": p.status,
        "base_amount": p.base_amount,
        "igv_amount": p.igv_amount,
        "total_amount": p.total_amount,
        "pdf_url": p.pdf_url,
        "voucher_url": getattr(p, "voucher_url", None),
        "contract_url": getattr(p, "contract_url", None),
        "dj_url": getattr(p, "dj_url", None),
        "provider_name": p.provider_name,
        "product_brand": p.product_brand,
        "product_model": p.product_model,
        "product_serial": p.product_serial,
        "product_condition": getattr(p, "product_condition", None),
        "items": [
            {
                "id": it.id,
                "category": it.category,
                "brand": it.brand,
                "model": it.model,
                "serial": it.serial,
                "specs": it.specs,
                "cost": it.cost,
            } for it in (p.items or [])
        ],
        "seller_id": getattr(p, "seller_id", None),
        "seller_doc_number": seller.doc_number if seller else None,
        "seller_full_name": seller.full_name if seller else None,
        "seller_address": seller.address if seller else None,
        "seller_civil_status": seller.civil_status if seller else None,
        "intermediary_id": getattr(p, "intermediary_id", None),
        "intermediary_name": intermediary.name if intermediary else None,
        "intermediary_doc_number": intermediary.doc_number if intermediary else None,
        "intermediary_ruc_number": intermediary.ruc_number if intermediary else None,
        "intermediary_address": intermediary.address if intermediary else None,
    }


@router.get("", response_model=list[PurchaseOut])
async def list_purchases(
    session: AsyncSession = Depends(get_session),
    type: str | None = Query(None),
    status: str | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
):
    stmt = select(Purchase).options(selectinload(Purchase.items))
    if type:
        stmt = stmt.where(Purchase.type == type)
    if status:
        stmt = stmt.where(Purchase.status == status)
    if q:
        stmt = stmt.where(Purchase.document_number.like(f"%{q}%"))
    stmt = stmt.offset(offset).limit(limit)
    result = await session.execute(stmt)
    purchases = result.scalars().all()
    out = []
    for p in purchases:
        out.append(await _map_purchase_out(p, session))
    return out


@router.post("", response_model=PurchaseOut)
async def create_purchase(payload: PurchaseCreate, session: AsyncSession = Depends(get_session)):
    body = payload.model_dump()
    items_payload = body.pop("items", [])
    seller_fields = {
        "doc_number": body.pop("seller_doc_number", None),
        "full_name": body.pop("seller_full_name", None),
        "address": body.pop("seller_address", None),
        "civil_status": body.pop("seller_civil_status", None),
    }
    p = Purchase(**body)
    if seller_fields["doc_number"] and seller_fields["full_name"]:
        exists = await session.execute(select(Seller).where(Seller.doc_number == seller_fields["doc_number"]))
        s = exists.scalars().first()
        if not s:
            s = Seller(**{k: v for k, v in seller_fields.items() if v is not None})
            session.add(s)
            await session.commit()
            await session.refresh(s)
        p.seller_id = s.id
        # Attach seller fields to output convenience
        p.provider_name = s.full_name if not p.provider_name else p.provider_name
    session.add(p)
    await session.commit()
    await session.refresh(p)
    for it in items_payload:
        item = PurchaseItem(purchase_id=p.id, **it)
        session.add(item)
    if items_payload:
        await session.commit()
    result = await session.execute(select(Purchase).options(selectinload(Purchase.items)).where(Purchase.id == p.id))
    p2 = result.scalars().first()
    return await _map_purchase_out(p2, session)


@router.put("/{purchase_id}", response_model=PurchaseOut)
async def update_purchase(purchase_id: int, payload: PurchaseUpdate, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Purchase).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p:
        return p
    data = payload.model_dump(exclude_unset=True)
    items_payload = data.pop("items", None)
    for k, v in data.items():
        setattr(p, k, v)
    if items_payload is not None:
        await session.execute(delete(PurchaseItem).where(PurchaseItem.purchase_id == p.id))
        for it in items_payload:
            session.add(PurchaseItem(purchase_id=p.id, **it))
    await session.commit()
    result = await session.execute(select(Purchase).options(selectinload(Purchase.items)).where(Purchase.id == p.id))
    p2 = result.scalars().first()
    return await _map_purchase_out(p2, session)


@router.delete("/{purchase_id}")
async def delete_purchase(purchase_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Purchase).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p:
        return {"deleted": False}
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
    def try_unlink(u: str | None):
        if not u:
            return
        fname = os.path.basename(u)
        fp = base_dir / fname
        if fp.exists():
            try:
                fp.unlink()
            except Exception:
                pass
    try_unlink(p.pdf_url)
    try_unlink(p.voucher_url)
    try_unlink(p.contract_url)
    try_unlink(p.dj_url)
    await session.delete(p)
    await session.commit()
    return {"deleted": True}


@router.post("/{purchase_id}/upload")
async def upload_purchase_file(
    purchase_id: int,
    file: UploadFile = File(...),
    doc_kind: str = Form("general"),
    request: Request = None,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Purchase).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    content_type = (file.content_type or "").lower()
    if not (content_type.startswith("application/pdf") or content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Solo se aceptan PDF o imágenes")
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
    base_dir.mkdir(parents=True, exist_ok=True)
    def slug(s: str | None):
        if not s:
            return ""
        return "".join(ch.lower() if ch.isalnum() or ch in ("-", "_") else "-" for ch in s).strip("-")
    ts = time.strftime("%Y%m%d%H%M%S")
    ext = os.path.splitext(file.filename or "")[1].lower() or ".pdf"
    doc = doc_kind.lower()
    if doc not in ("voucher", "contract", "dj", "general"):
        doc = "general"
    meta = [
        f"ruc10-{purchase_id}",
        doc,
        slug(p.document_number),
        slug(p.provider_name),
        slug(p.product_brand),
        slug(p.product_model),
        slug(p.product_serial),
        ts,
    ]
    safe_name = "-".join([m for m in meta if m]) + ext
    dst = base_dir / safe_name
    data = await file.read()
    dst.write_bytes(data)
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/files/purchases/{safe_name}"
    if doc == "voucher":
        p.voucher_url = url
    elif doc == "contract":
        p.contract_url = url
    elif doc == "dj":
        p.dj_url = url
    else:
        p.pdf_url = url
    await session.commit()
    return {"url": url, "filename": safe_name, "doc_kind": doc}


@router.get("/{purchase_id}/download")
async def download_purchase_file(purchase_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Purchase).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p or not p.pdf_url:
        raise HTTPException(status_code=404, detail="Sustento no disponible")
    fname = os.path.basename(p.pdf_url)
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
    file_path = base_dir / fname
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(path=str(file_path), filename=fname)


@router.get("/{purchase_id}/download/{doc_kind}")
async def download_purchase_file_kind(purchase_id: int, doc_kind: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Purchase).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    doc = doc_kind.lower()
    url = None
    if doc == "voucher":
        url = p.voucher_url
    elif doc == "contract":
        url = p.contract_url
    elif doc == "dj":
        url = p.dj_url
    else:
        url = p.pdf_url
    if not url:
        raise HTTPException(status_code=404, detail="Sustento no disponible")
    fname = os.path.basename(url)
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
    file_path = base_dir / fname
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(path=str(file_path), filename=fname)


@router.post("/{purchase_id}/generate/{doc_kind}")
async def generate_document(purchase_id: int, doc_kind: str, request: Request, session: AsyncSession = Depends(get_session)):
    doc_kind = doc_kind.lower()
    if doc_kind not in ("contract", "dj"):
        raise HTTPException(status_code=400, detail="Tipo de documento inválido")
    result = await session.execute(select(Purchase).options(selectinload(Purchase.items)).where(Purchase.id == purchase_id))
    p = result.scalars().first()
    if not p:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    seller = None
    if getattr(p, "seller_id", None):
        sres = await session.execute(select(Seller).where(Seller.id == p.seller_id))
        seller = sres.scalars().first()
    intermediary = None
    if getattr(p, "intermediary_id", None):
        ires = await session.execute(select(Intermediary).where(Intermediary.id == p.intermediary_id))
        intermediary = ires.scalars().first()
    def safe(val: str | None): return val or ""
    def fmt_date_es(d: datetime | None):
        m = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
        dt = d or datetime.utcnow()
        return f"{dt.day} de {m[dt.month-1]} del año {dt.year}"
    def curr(v: float | int | None):
        if v is None: return "S/ 0.00"
        return f"S/ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    cat = safe(p.items[0].category if hasattr(p, "items") and p.items else None)
    brand = safe(p.product_brand)
    model = safe(p.product_model)
    serial = safe(p.product_serial)
    cond = safe(p.product_condition)
    fecha_str = fmt_date_es(p.date if isinstance(p.date, datetime) else datetime.utcnow())
    base_str = curr(p.base_amount)
    notary_val = (p.total_amount or 0) - (p.base_amount or 0)
    notary_str = curr(notary_val)
    total_str = curr(p.total_amount)
    if doc_kind == "contract":
        content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Contrato de Compra-Venta</title>
<style>
@page {{ size: A4; margin: 2.2cm; }}
body {{ font-family: Arial, sans-serif; font-size: 13.2px; line-height: 1.45; color: #000; }}
h2 {{ text-align: center; text-transform: uppercase; margin-bottom: 10px; }}
p {{ margin: 5px 0; text-align: justify; }}
.firmas {{ margin-top: 28px; display: flex; justify-content: space-between; text-align: center; width: 100%; }}
.firma {{ width: 48%; }}
.linea {{ border-top: 1px solid #000; margin: 40px 0 5px 0; width: 100%; }}
.huella {{ font-size: 12px; margin-top: 4px; }}
.footer {{ margin-top: 15px; font-size: 10.5px; color: #555; text-align: center; }}
.space {{ height: 100px; }}
@media print {{ body {{ margin: 0; }} }}
</style>
</head>
<body>
<h2>Contrato de Compra-Venta</h2>
<p><strong>Fecha:</strong> {fecha_str}</p>
<p>Conste por el presente documento el <strong>Contrato de Compra-Venta</strong> que celebran, de una parte el <strong>PROPIETARIO (VENDEDOR)</strong> y, de la otra, el <strong>COMPRADOR (INTERMEDIARIO)</strong>, conforme a las cláusulas siguientes:</p>
<p><strong>PRIMERA: DATOS DEL VENDEDOR</strong></p>
<p>Nombre: {safe(p.provider_name) or safe(seller.full_name if seller else None)}.<br>DNI: {safe(seller.doc_number if seller else None)}.<br>Dirección: {safe(seller.address if seller else None)}.<br>Estado civil: {safe(seller.civil_status if seller else None)}.</p>
<p><strong>SEGUNDA: DATOS DEL COMPRADOR (INTERMEDIARIO)</strong></p>
<p>Nombre: {safe(intermediary.name if intermediary else None)}.<br>Documento / RUC: {safe(intermediary.doc_number if intermediary else None)} / {safe(intermediary.ruc_number if intermediary else None)}.<br>Dirección: {safe(intermediary.address if intermediary else None)}.</p>
<p><strong>TERCERA: DESCRIPCIÓN DEL EQUIPO</strong></p>
<p>Categoría: {cat}. Marca: {brand}. Modelo: {model}.<br>Número de serie: {serial}. Condición: {cond}.</p>
<p><strong>CUARTA: PRECIO Y ACUERDO COMERCIAL</strong></p>
<p>El precio de venta asciende a la suma de <strong>{base_str}</strong>, monto que el COMPRADOR declara haber cancelado en su totalidad. Los gastos notariales ascienden a {notary_str}, siendo el total <strong>{total_str}</strong>.</p>
<p><strong>QUINTA: DECLARACIONES</strong></p>
<p>El VENDEDOR declara ser legítimo propietario del bien descrito, libre de cargas o gravámenes. El COMPRADOR declara haber revisado y aceptado el equipo conforme.</p>
<p><strong>SEXTA: CONFORMIDAD</strong></p>
<p>Leído que fue el presente contrato, ambas partes lo firman en señal de conformidad en la fecha indicada.</p>
<div class="space"></div>
<div class="firmas">
<div class="firma"><div class="linea"></div><strong>VENDEDOR</strong><br>Nombre: {safe(p.provider_name) or safe(seller.full_name if seller else None)}<br>DNI: {safe(seller.doc_number if seller else None)}<div class="huella">Huella Digital</div></div>
<div class="firma"><div class="linea"></div><strong>COMPRADOR / INTERMEDIARIO</strong><br>Nombre: {safe(intermediary.name if intermediary else None)}<br>DNI / RUC: {safe(intermediary.doc_number if intermediary else None)} / {safe(intermediary.ruc_number if intermediary else None)}<div class="huella">Huella Digital</div></div>
</div>
</body>
</html>"""
    else:
        content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Declaración Jurada de Origen</title>
<style>
@page {{ size: A4; margin: 2.2cm; }}
body {{ font-family: Arial, sans-serif; font-size: 13.2px; line-height: 1.45; color: #000; }}
h2 {{ text-align: center; text-transform: uppercase; margin-bottom: 10px; }}
p {{ margin: 5px 0; text-align: justify; }}
.firma {{ margin-top: 35px; text-align: center; }}
.linea {{ border-top: 1px solid #000; margin: 45px auto 6px auto; width: 70%; }}
.huella {{ font-size: 12px; margin-top: 4px; }}
.footer {{ margin-top: 18px; font-size: 10.5px; color: #555; text-align: center; }}
.space {{ height: 100px; }}
@media print {{ body {{ margin: 0; }} }}
</style>
</head>
<body>
<h2>Declaración Jurada de Origen</h2>
<p><strong>Fecha:</strong> {fecha_str}</p>
<p>Yo, <strong>{safe(p.provider_name) or safe(seller.full_name if seller else None)}</strong>, identificado con Documento Nacional de Identidad (DNI) N.º <strong>{safe(seller.doc_number if seller else None)}</strong>, con domicilio en <strong>{safe(seller.address if seller else None)}</strong>, de estado civil <strong>{safe(seller.civil_status if seller else None)}</strong>, declaro bajo juramento lo siguiente:</p>
<p><strong>PRIMERA: DECLARACIÓN DE PROPIEDAD</strong></p>
<p>Declaro ser único y legítimo propietario del bien descrito en la presente declaración, el cual ha sido obtenido de manera lícita, sin vulnerar derechos de terceros y conforme a la normativa vigente.</p>
<p><strong>SEGUNDA: DESCRIPCIÓN DEL BIEN</strong></p>
<p>Categoría: {cat}. Marca: {brand}. Modelo: {model}. Número de serie: {serial}. Condición: {cond}.</p>
<p><strong>TERCERA: RESPONSABILIDAD</strong></p>
<p>Declaro que el bien no se encuentra reportado como robado, extraviado, ni vinculado a actividades ilícitas. Asumo plena responsabilidad civil, administrativa y penal en caso de que la presente declaración resulte falsa.</p>
<p><strong>CUARTA: FINALIDAD</strong></p>
<p>La presente Declaración Jurada se emite para los fines legales que correspondan, sirviendo como constancia del origen y propiedad del bien descrito.</p>
<p><strong>QUINTA: CONFORMIDAD</strong></p>
<p>Firmo la presente declaración en señal de conformidad, en la fecha indicada.</p>
<div class="space"></div>
<div class="firma">
  <div class="linea"></div>
  <strong>DECLARANTE</strong><br>
  Nombre: {safe(p.provider_name) or safe(seller.full_name if seller else None)}<br>
  DNI: {safe(seller.doc_number if seller else None)}
  <div class="huella">Huella Digital</div>
</div>
</body>
</html>"""
    base_dir = Path(__file__).resolve().parents[1] / "uploads" / "purchases"
    base_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d%H%M%S")
    def slug(s: str | None):
        if not s: return ""
        return "".join(ch.lower() if ch.isalnum() or ch in ("-", "_") else "-" for ch in s).strip("-")
    safe_name = f"ruc10-{purchase_id}-{doc_kind}-{slug(p.product_serial)}-{ts}.html"
    file_path = base_dir / safe_name
    file_path.write_text(content, encoding="utf-8")
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/files/purchases/{safe_name}"
    return {"url": url, "filename": safe_name, "doc_kind": doc_kind}
