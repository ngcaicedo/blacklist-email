from sqlmodel import SQLModel

from adapters.models import Blacklist

Base = SQLModel

__all__ = ["Base", "Blacklist"]
