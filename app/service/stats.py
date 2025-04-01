from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user
from app.service.schemas import LinkStats

from app.db import get_db
from app.models import Link

stats_router = APIRouter(tags=["Stats"])

@stats_router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(
        short_url: str,
        db: Session = Depends(get_db)
):
    link: Optional[Link] = db.query(Link).filter_by(short_url = short_url).first()

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.user_id and (not current_user or current_user != link.user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return link