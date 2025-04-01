import os
from config import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker

Base = declarative_base()

# Async
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# Sync
engine = create_sync_engine(DATABASE_URL)
SessionLocal = sync_sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Init db
async def init_db():
    async with async_engine.begin() as conn:
        from app.models import Base
        await conn.run_sync(Base.metadata.create_all)