import uuid
from enum import unique
from datetime import datetime
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column


Base = declarative_base()

class User(SQLAlchemyBaseUserTable, Base):
    __tablename__ = "users"

    id: int = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login: str = Column(String, unique=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)

    links = relationship("Link", back_populates="user")


class Link(Base):
    __tablename__ = "links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    long_url = Column(String, nullable=False)
    short_url = Column(String(20), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    click_count = Column(Integer, default=0)
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="links")
