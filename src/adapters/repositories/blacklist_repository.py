from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from adapters.models import Blacklist
from domain.ports import BlacklistRepository


class SQLModelBlacklistRepository(BlacklistRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_email(
        self,
        email: str,
        app_uuid: UUID,
        blocked_reason: Optional[str],
        ip_address: str,
    ) -> Blacklist:
        blacklist_entry = Blacklist(
            email=email,
            app_uuid=app_uuid,
            blocked_reason=blocked_reason,
            ip_address=ip_address,
        )
        self.session.add(blacklist_entry)
        await self.session.commit()
        await self.session.refresh(blacklist_entry)
        return blacklist_entry

    async def get_by_email(self, email: str) -> Optional[Blacklist]:
        statement = select(Blacklist).where(Blacklist.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        result = await self.get_by_email(email)
        return result is not None

