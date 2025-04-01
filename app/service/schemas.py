from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


# stats
class LinkStats(BaseModel):
    is_active: Optional[bool] = True
    long_url: str
    created_at: datetime
    expires_at: datetime
    click_count: int
    last_used_at: Optional[datetime]

    model_config = {"from_attributes": True}


# links
class LinkCreate(BaseModel):
    long_url: HttpUrl
    custom_alias: Optional[str] = Field(None, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    expires_at: Optional[datetime] = None


class LinkInfo(BaseModel):
    short_url: HttpUrl
    long_url: HttpUrl
    expires_at: Optional[datetime] = None
    is_active: Optional[bool]

    model_config = {"from_attributes": True}


class LinkUpdate(BaseModel):
    long_url: Optional[HttpUrl] = None
    custom_alias: Optional[str] = Field(None, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    expires_at: Optional[datetime] = None