from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings


class Database:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.db_url
        self._async_engine: Optional[AsyncEngine] = None

    @property
    def async_engine(self) -> AsyncEngine:
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.database_url,
                echo=settings.db_echo,
                future=True,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        return self._async_engine

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency for FastAPI to inject async sessions."""
        async with AsyncSession(self.async_engine, expire_on_commit=False) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Close database connection."""
        if self._async_engine:
            await self._async_engine.dispose()


# Global database instance
database = Database()
