from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from adapters.models import Blacklist


class BlacklistRepository(ABC):
    @abstractmethod
    async def add_email(
        self,
        email: str,
        app_uuid: UUID,
        blocked_reason: Optional[str],
        ip_address: str,
    ) -> Blacklist:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Blacklist]:
        pass
    
    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        pass

