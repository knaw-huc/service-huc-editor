from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from src.auth.authentication import UserDep

router = APIRouter(
    prefix="/app/{app}/auth"
)


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