import logging
import os
from datetime import timedelta, datetime, timezone
from typing import Optional, Annotated

import jwt
import toml
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic, \
    OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.apache import HtpasswdFile
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from pydantic import BaseModel
from saxonche import PySaxonProcessor
from sqlmodel import Session, select
from starlette import status

from src.database import SessionDep
from src.auth.models import User
from src.commons import settings, api_keys
from src.config.dependencies import ConfigDep

bearer_security = HTTPBearer(auto_error=False)
basic_auth = HTTPBasic(auto_error=False)

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD = password_hash.hash("dummy")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"


class InvalidCredentialsException(Exception):
    """
    Used when the credentials of the user are invalid
    """


class UnknownApiKeyException(Exception):
    """
    Used when the api key is unknown.
    """


class TokenData(BaseModel):
    username: str | None = None


def create_user(session: Session, username: str, password: str):
    """
    Create a new user
    """
    user = User(
        name=username,
        password_hash=get_password_hash(password),
    )
    session.add(user)
    session.commit()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the password is correct
    """
    return password_hash.verify(plain_password, hashed_password)


def verify_legacy(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a legacy password using HtpasswdFile
    """
    ht = HtpasswdFile.from_string(f"verify:{hashed_password}")
    return ht.check_password("verify", plain_password)


def get_password_hash(password: str) -> str:
    """
    Hash the password
    """
    return password_hash.hash(password)


def initialize_users(app, config: ConfigDep, session: SessionDep):
    """
    Create users for the app if they haven't been added yet.
    """
    logging.info("Initializing users")
    if 'access' in config["app"] and 'users' in config["app"]["access"]:
        logging.info("Htp file present, importing legacy users")
        import_from_htpasswd(app, config, session)

    if 'access' in config["app"] and 'users_csv' in config["app"]["access"]:
        logging.info("CSV file present, importing users")


def import_from_htpasswd(app: str, config: ConfigDep, session: SessionDep):
    """
    Import users from a htpasswd file
    """
    users_cred_file = config['app']['access']['users']
    users_cred_file = os.path.normpath(os.path.join(f"{settings.URL_DATA_APPS}/{app}/", users_cred_file))
    if not os.path.isfile(users_cred_file):
        logging.warning("Configured htp file is missing. Skipping import of users")
        logging.warning(f"File: {users_cred_file}")
        return

    logging.info("Found htp file, importing users from it")
    ht = HtpasswdFile(users_cred_file)
    for u in ht.users():
        user: Optional[User] = session.exec(select(User).where(User.name == u)).first()
        if not user:
            user = User(name=u, password_hash=ht.get_hash(u))
            session.add(user)
    session.commit()


def get_user_with_password(username: str, password: str, session: SessionDep):
    """
    Get user based on username and password
    """
    user: Optional[User] = session.exec(select(User).where(User.name == username)).first()
    if user:
        try:
            if not verify_password(password, user.password_hash):
                raise InvalidCredentialsException
            return user
        except UnknownHashError:
            logging.warning("Unknown hash for user")
            logging.warning(user)
            if verify_legacy(password, user.password_hash.decode()):
                print("Updating old hash")
                user.password_hash = get_password_hash(password)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user

    verify_password(password, DUMMY_PASSWORD)
    raise InvalidCredentialsException



def get_current_user_basic(
        app: str,
        session: SessionDep,
        credentials: HTTPBasicCredentials = Depends(basic_auth)) -> User:
    """
    Get the current user using HTTP Basic Authentication
    :param app: The app
    :param session: The session
    :param credentials: The credentials
    """
    try:
        return get_user_with_password(credentials.username, credentials.password, session)
    except InvalidCredentialsException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})


def get_user_with_app(
        app: str,
        session: SessionDep,
        basic_credentials: Optional[HTTPBasicCredentials] = Depends(basic_auth),
        bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security),
) -> Optional[User]:
    """
    Get the current user of this app. Uses HTTP Basic Authentication initially, and if that fails it will check if there's
    a header token present.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if basic_credentials:
        return get_current_user_basic(app, session, basic_credentials)
    elif bearer_credentials:
        # Handle bearer token authentication. This can either be a fixed api key, or an OAuth2 token
        token = bearer_credentials.credentials
        try:
            return check_api_key(token, app)
        except UnknownApiKeyException:
            # Not in legacy api keys. Treat as JWT
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get('sub')
                if username is None:
                    raise credentials_exception
                token_data = TokenData(username=username)
            except InvalidTokenError:
                raise credentials_exception
            user = session.exec(select(User).where(User.name == token_data.username)).first()
            if user is None:
                raise credentials_exception
            return user

    else:
        return None


UserDep = Annotated[User, Depends(get_user_with_app)]


def check_api_key(token: str, app: str) -> User:
    """
    Check if the token is one of the registered API keys and return the corresponding User.
    """
    if token not in api_keys:
        raise UnknownApiKeyException
    return def_user(app)


def allowed(user: Optional[User], app: str, action: str, default: str, prof=None, nr=None):
    """
    :param user: The user
    :param app: The app
    :param action: The action
    :param default: The default mode
    :param prof: The profile
    :param nr: The record number/id
    """
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(config_app_file):
        logging.error(f"config file {config_app_file} doesn't exist")
        if default == "any":
            return True
        return False
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        mode = default
        if 'access' in config["app"]:
            if action in config['app']['access']:
                mode = config['app']['access'][action]
        if mode == "owner" and user is not None and prof is not None and nr is not None:
            record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
            with open(record_file, 'r') as file:
                rec = file.read()
                with PySaxonProcessor(license=False) as proc:
                    rec = proc.parse_xml(xml_text=rec)
                    xpproc = proc.new_xpath_processor()
                    xpproc.set_cwd(os.getcwd())
                    xpproc.declare_namespace('clariah','http://www.clariah.eu/')
                    xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')
                    xpproc.set_context(xdm_item=rec)
                    owner = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()
                    if owner == user.name:
                        return True
        elif mode == "owner" and user is not None:
                return True
        elif mode == "users" and user is not None:
            return True
        elif mode == "any":
            return True
    return False


def def_user(app: str) -> User:
    """
    Get the default user for the application.
    :param app: The app for which the default user should be returned
    """
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        if 'def_user' in config["app"]:
            return User(name=config["app"]['def_user'])
        elif 'def_user' in settings:
            return User(name=settings.def_user)
        return User(name="server")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
