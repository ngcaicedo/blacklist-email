from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class Blacklist(SQLModel, table=True):
    __tablename__ = "blacklists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    app_uuid: UUID = Field(nullable=False)
    blocked_reason: Optional[str] = Field(default=None, max_length=255)
    ip_address: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

