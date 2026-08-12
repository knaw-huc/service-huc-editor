from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette import status

from src.auth.authentication import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.database import SessionDep
from src.auth.authentication import UserDep, get_user_with_password, InvalidCredentialsException


router = APIRouter(
    prefix="/app/{app}/auth"
)


class Token(BaseModel):
    """
    Response for JWT token
    """
    access_token: str
    token_type: str


@router.post("/token")
async def login_for_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 flow: get JWT
    """
    try:
        user = get_user_with_password(form_data.username, form_data.password, session)
    except InvalidCredentialsException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.name}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


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