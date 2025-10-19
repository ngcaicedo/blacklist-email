from domain.ports import BlacklistRepository
from domain.schemas import BlacklistCheckResponse
from domain.use_cases.base_use_case import BaseUseCase


class CheckEmailInBlacklistUseCase(BaseUseCase[str, BlacklistCheckResponse]):
    def __init__(self, repository: BlacklistRepository):
        self.repository = repository

    async def execute(self, email: str) -> BlacklistCheckResponse:
        blacklist_entry = await self.repository.get_by_email(email)
        
        if blacklist_entry:
            return BlacklistCheckResponse(
                email=email,
                is_blocked=True,
                blocked_reason=blacklist_entry.blocked_reason,
                blocked_at=blacklist_entry.created_at,
            )
        
        return BlacklistCheckResponse(
            email=email,
            is_blocked=False,
            blocked_reason=None,
            blocked_at=None,
        )

