from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import create_engine, Session

from src.commons import settings


def get_db_eng_for_app(app: str):
    sqlite_filename = f"{settings.URL_DATA_APPS}/{app}/database.db"
    sqlite_url = f"sqlite:///{sqlite_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, connect_args=connect_args)

EngineDep = Annotated[Engine, Depends(get_db_eng_for_app)]


def get_session(engine: EngineDep):
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]