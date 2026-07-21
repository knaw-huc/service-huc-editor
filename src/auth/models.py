from uuid import uuid4

from sqlalchemy.orm import mapped_column, Mapped

from src.database.models import Base


class User(Base):
    """
    The user model for authentication
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(default=None, primary_key=True)
    name: Mapped[str] = mapped_column(index=True, unique=True)
    password_hash: Mapped[str]


class RefreshToken(Base):
    """
    The refresh token model for authentication
    """
    __tablename__ = "refresh_token"

    id: Mapped[str] = mapped_column(index=True, unique=True, primary_key=True)
    username: Mapped[str] = mapped_column(index=True)

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
        super().__init__(**kwargs)