from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from datetime import datetime, timezone

from portfolio.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
