"""
Functions for dealing with the database.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from src.commons import settings


def get_db_eng_for_app(app: str):
    """
    Get the database engine for given app.
    :param app:
    :param cache: If true returns the cache db instead of the regular one
    :return:
    """
    sqlite_filename = f"{settings.URL_DATA_APPS}/{app}/database.db"
    sqlite_url = f"sqlite:///{sqlite_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, connect_args=connect_args)

EngineDep = Annotated[Engine, Depends(get_db_eng_for_app)]


def get_cache_eng_for_app(app: str):
    """
    Get the database engine for given app.
    :param app:
    :param cache: If true returns the cache db instead of the regular one
    :return:
    """
    sqlite_filename = f"{settings.URL_DATA_APPS}/{app}/cache.db"
    sqlite_url = f"sqlite:///{sqlite_filename}"
    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, connect_args=connect_args)

CacheDep = Annotated[Engine, Depends(get_cache_eng_for_app)]


def get_session(engine: EngineDep):
    """
    Get a database session.
    :param engine:
    :return:
    """
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def get_cache_session(engine: CacheDep):
    """
    Get a cache database session
    :param engine:
    :return:
    """
    with Session(engine) as session:
        yield session

CacheSessionDep = Annotated[Session, Depends(get_cache_session)]