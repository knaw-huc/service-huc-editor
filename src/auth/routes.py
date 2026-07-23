"""
Authentication related routes
"""

from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy import select
from starlette import status

from src.auth.authentication import REFRESH_TOKEN_EXPIRE_MINUTES, ALGORITHM, sign_url
from src.auth.models import RefreshToken
from src.auth.authentication import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.commons import settings
from src.database.database import SessionDep
from src.auth.authentication import UserDep, get_user_with_password, InvalidCredentialsException


router = APIRouter(
    prefix="/app/{app}/auth"
)


class Token(BaseModel):
    """
    Response for JWT token
    """
    access_token: str
    refresh_token: str
    token_type: str


@router.post("/token")
async def login_for_access_token(session: SessionDep,
                                 form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 flow: get JWT
    """
    try:
        user = get_user_with_password(form_data.username, form_data.password, session)
    except InvalidCredentialsException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"}) from e

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token_obj = RefreshToken(username=user.name)
    session.add(refresh_token_obj)
    session.commit()

    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    refresh = create_access_token(data={"sub": user.name, "uuid": refresh_token_obj.id}, expires_delta=refresh_token_expires)
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh)


class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_token(data: RefreshRequest, session: SessionDep):
    """
    OAuth2 flow: refresh token
    :param data:
    :param session:
    :return:
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Invalid credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(data.refresh_token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_id = payload.get("uuid")
        if username is None or token_id is None:
            raise credentials_exception
    except InvalidTokenError as e:
        raise credentials_exception from e
    token = session.scalars(select(RefreshToken).where(RefreshToken.id == token_id and RefreshToken.username == username)).first()
    if not token:
        raise credentials_exception
    session.delete(token)

    refresh_token_obj = RefreshToken(username=username)
    session.add(refresh_token_obj)
    session.commit()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    refresh = create_access_token(data={"sub": username, "uuid": refresh_token_obj.id}, expires_delta=refresh_token_expires)
    return Token(access_token=access_token, token_type="bearer", refresh_token=refresh)


class UrlSignRequest(BaseModel):
    url: str
    method: str = "GET"

@router.post("/sign")
async def generate_signed_url(sign_request: UrlSignRequest,  user: UserDep):
    """
    Generate a signed url
    :return:
    """
    signed = sign_url(sign_request.url, user, sign_request.method)
    return {
        "url": signed,
        "method": sign_request.method,
    }


@router.get("/me")
async def me(user: UserDep):
    """
    Get user info
    """
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {
        "id": user.id,
        "name": user.name,
    }
