from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.models import Offer, OfferItem, Product, User
from app.schemas.schemas import OfferCreate, OfferOut, OfferUpdate, OfferItemCreate, OfferItemOut, OfferItemUpdate


router = APIRouter()


@router.get("/", response_model=List[OfferOut])
async def list_offers(
    lead_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Offer).order_by(Offer.created_at.desc())
    if lead_id:
        stmt = stmt.where(Offer.lead_id == lead_id)
    if client_id:
        stmt = stmt.where(Offer.client_id == client_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=OfferOut, status_code=201)
async def create_offer(
    payload: OfferCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    offer = Offer(**payload.model_dump(), created_by=user.id)
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return offer


@router.get("/{offer_id}", response_model=OfferOut)
async def get_offer(offer_id: str, db: AsyncSession = Depends(get_db)):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    return offer


@router.get("/{offer_id}/items", response_model=List[OfferItemOut])
async def list_offer_items(offer_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(OfferItem).where(OfferItem.offer_id == offer_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{offer_id}/items", response_model=OfferItemOut, status_code=201)
async def add_offer_item(
    offer_id: str,
    payload: OfferItemCreate,
    db: AsyncSession = Depends(get_db),
):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")

    product = await db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    qty = max(1, int(payload.quantity or 1))
    unit_price = float(payload.unit_price if payload.unit_price is not None else product.unit_price or 0.0)
    line_total = qty * unit_price

    item = OfferItem(
        offer_id=offer_id,
        product_id=payload.product_id,
        quantity=qty,
        unit_price=unit_price,
        line_total=line_total,
        description=payload.description,
    )
    db.add(item)
    offer.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{offer_id}", response_model=OfferOut)
async def update_offer(offer_id: str, payload: OfferUpdate, db: AsyncSession = Depends(get_db)):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(offer, k, v)
    offer.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(offer)
    return offer


@router.patch("/{offer_id}/items/{item_id}", response_model=OfferItemOut)
async def update_offer_item(
    offer_id: str,
    item_id: str,
    payload: OfferItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    item = await db.get(OfferItem, item_id)
    if not item or item.offer_id != offer_id:
        raise HTTPException(404, "Offer item not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)

    qty = max(1, int(item.quantity or 1))
    unit_price = float(item.unit_price or 0.0)
    item.quantity = qty
    item.unit_price = unit_price
    item.line_total = qty * unit_price

    offer = await db.get(Offer, offer_id)
    if offer:
        offer.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{offer_id}/items/{item_id}", status_code=204)
async def delete_offer_item(offer_id: str, item_id: str, db: AsyncSession = Depends(get_db)):
    item = await db.get(OfferItem, item_id)
    if not item or item.offer_id != offer_id:
        raise HTTPException(404, "Offer item not found")
    await db.delete(item)

    offer = await db.get(Offer, offer_id)
    if offer:
        offer.updated_at = datetime.utcnow()

    await db.commit()

