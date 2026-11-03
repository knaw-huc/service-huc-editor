import fcntl
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine, Session

from src.commons import settings


def get_db_eng_for_app(app: str):
    sqlite_filename = f"{settings.URL_DATA_APPS}/{app}/database.db"
    sqlite_url = f"sqlite:///{sqlite_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, connect_args=connect_args)


def initialize_app_database(app: str):
    from src.auth.authentication import initialize_users
    from src.config.dependencies import get_app_configuration

    engine = get_db_eng_for_app(app)
    lock_path = f"{settings.URL_DATA_APPS}/{app}/database.db.lock"
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            initialize_users(app, get_app_configuration(app), session)


EngineDep = Annotated[Engine, Depends(get_db_eng_for_app)]


def get_session(engine: EngineDep):
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]