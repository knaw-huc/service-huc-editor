from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from src.auth.models import User
from src.auth.authentication import allowed, get_user_with_app
from src.config.dependencies import ConfigDep

router = APIRouter(
    prefix="/app/{app}/profiles"
)

@router.get("/")
async def get_profiles(app: str, config: ConfigDep, user: Optional[User] = Depends(get_user_with_app)):
    """
    Get all available profiles
    :param user:
    :param app:
    :param config:
    :return:
    """
    if not allowed(user, app, 'read', 'any'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!",
                            headers={"WWW-Authenticate": "Bearer"})
    profiles = config['app']['prof']
    return profiles
