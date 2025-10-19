from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class BlacklistCreateRequest(BaseModel):
    email: EmailStr
    app_uuid: UUID
    blocked_reason: Optional[str] = Field(None, max_length=255)


class BlacklistCreateResponse(BaseModel):
    message: str
    email: str
    blocked_at: datetime


class BlacklistCheckResponse(BaseModel):
    email: str
    is_blocked: bool
    blocked_reason: Optional[str] = None
    blocked_at: Optional[datetime] = None

