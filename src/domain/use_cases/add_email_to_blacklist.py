from uuid import UUID

from domain.ports import BlacklistRepository
from domain.schemas import BlacklistCreateRequest, BlacklistCreateResponse
from domain.use_cases.base_use_case import BaseUseCase
from errors import DuplicateEmailError


class AddEmailToBlacklistUseCase(BaseUseCase[BlacklistCreateRequest, BlacklistCreateResponse]):
    def __init__(self, repository: BlacklistRepository):
        self.repository = repository

    async def execute(
        self, request: BlacklistCreateRequest, ip_address: str
    ) -> BlacklistCreateResponse:
        email_exists = await self.repository.email_exists(request.email)
        if email_exists:
            raise DuplicateEmailError(f"Email {request.email} already exists in blacklist")
        
        blacklist_entry = await self.repository.add_email(
            email=request.email,
            app_uuid=request.app_uuid,
            blocked_reason=request.blocked_reason,
            ip_address=ip_address,
        )
        
        return BlacklistCreateResponse(
            message="Email added to blacklist successfully",
            email=blacklist_entry.email,
            blocked_at=blacklist_entry.created_at,
        )

