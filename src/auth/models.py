from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    The user model for authentication
    """
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    password_hash: str = Field(index=True)