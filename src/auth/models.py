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