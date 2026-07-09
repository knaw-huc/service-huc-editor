from typing import Any

from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base model for the regular database
    """
    pass


class CacheBase(DeclarativeBase):
    """
    Base model for the cache database
    """
    type_annotation_map = {
        dict[str, Any]: JSON
    }