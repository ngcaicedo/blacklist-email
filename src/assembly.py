from typing import AsyncGenerator

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from adapters.repositories import SQLModelBlacklistRepository
from db.session import database
from domain.ports import BlacklistRepository
from domain.use_cases import AddEmailToBlacklistUseCase, CheckEmailInBlacklistUseCase


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in database.get_async_session():
        yield session


def get_blacklist_repository(
    session: AsyncSession = Depends(get_session),
) -> BlacklistRepository:
    return SQLModelBlacklistRepository(session)


def get_add_email_use_case(
    repository: BlacklistRepository = Depends(get_blacklist_repository),
) -> AddEmailToBlacklistUseCase:
    return AddEmailToBlacklistUseCase(repository)


def get_check_email_use_case(
    repository: BlacklistRepository = Depends(get_blacklist_repository),
) -> CheckEmailInBlacklistUseCase:
    return CheckEmailInBlacklistUseCase(repository)

