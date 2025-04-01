from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List

from app.service.schemas import LinkCreate, LinkInfo, LinkUpdate
from app.models import Link
from app.db import get_db
from app.auth.user_manager import fastapi_users
from app.models import User
from app.service.src import generate_unique_short_code

links_router = APIRouter(tags=["create", "delete", "redirect", "update", "search", "set_expiration"])


@links_router.post("/shorten", response_model=LinkInfo)
def create_short_link(
    payload: LinkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(fastapi_users.current_user(optional=True))
) -> LinkInfo:
    if payload.custom_alias:
        if db.query(Link).filter_by(short_url=payload.custom_alias).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Alias already in use")
        short_url = payload.custom_alias
    else:
        short_url = generate_unique_short_code(db)

    now = datetime.now(timezone.utc)

    new_link = Link(
        long_url=str(payload.original_url),
        short_url=short_url,
        expires_at=payload.expires_at,
        created_at=now,
        updated_at=now,
        user_id=current_user.id if current_user else None,
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    full_short_url = f"{request.base_url.rstrip('/')}/{short_url}"

    return LinkInfo(
        short_url=full_short_url,
        original_url=new_link.long_url,
        expires_at=new_link.expires_at,
    )


@links_router.delete("/{short_url}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_link(
    short_url: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(fastapi_users.current_user(optional=True)),
):

    link = db.query(Link).filter_by(short_url=short_url).first()

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found")

    if link.user_id is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Anonymous links cannot be deleted")

    if not current_user or current_user.id != link.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this link")

    db.delete(link)
    db.commit()


@links_router.get("/{short_code}",
    response_class=RedirectResponse,
    status_code=302,
    include_in_schema=False,
)
def redirect_to_original(
    short_url: str,
    db: Session = Depends(get_db),
):
    link = db.query(Link).filter_by(short_url=short_url).first()

    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")

    if link.expires_at and link.expires_at < datetime.now():
        raise HTTPException(status_code=410, detail="Link has expired")

    link.click_count += 1
    link.last_used_at = datetime.now()
    db.commit()

    return RedirectResponse(link.long_url)


@links_router.get("/search", response_model=List[LinkInfo])
def search_links_by_original_url(
    request: Request,
    original_url: str = Query(..., description="Original URL for search"),
    db: Session = Depends(get_db)
):
    cleaned_input = original_url.rstrip("/").lower()

    links = db.query(Link).filter(
        func.lower(Link.long_url).like(f"{cleaned_input}%")
    ).all()

    if not links:
        raise HTTPException(status_code=404, detail="No links found for this original URL")

    base_url = str(request.base_url).rstrip("/")

    return [
        LinkInfo(
            short_url=f"{base_url}/{link.short_url}",
            original_url=link.long_url,
            expires_at=link.expires_at
        )
        for link in links
    ]


@links_router.put("/links/{short_url}", response_model=LinkInfo)
def update_short_link(
    short_url: str,
    payload: LinkUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(fastapi_users.current_user(optional=True)),
):
    link = db.query(Link).filter_by(short_code=short_url).first()

    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")

    if not link.user_id:
        raise HTTPException(status_code=403, detail="Anonymous links cannot be updated")

    if not current_user or current_user.id != link.user_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this link")

    if payload.long_url:
        link.long_url = str(payload.long_url)

    if payload.custom_alias:
        existing_link = db.query(Link).filter_by(custom_alias=payload.custom_alias).first()
        if existing_link:
            raise HTTPException(status_code=400, detail="Alias already in use")
        link.custom_alias = payload.custom_alias
        link.short_url = payload.custom_alias

    if payload.expires_at:
        link.expires_at = payload.expires_at

    db.commit()
    db.refresh(link)

    return LinkInfo(
        short_url=f"{link.short_url}",
        original_url=link.long_url,
        expires_at=link.expires_at,
    )