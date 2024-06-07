import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
import emoji
import importlib.metadata
from src.commons import settings, data
import importlib.metadata
import logging
from contextlib import asynccontextmanager

import emoji
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from src.commons import settings, data

__version__ = importlib.metadata.metadata(settings.SERVICE_NAME)["version"]

from starlette.middleware.cors import CORSMiddleware

from src import public, protected

api_keys = [
    settings.SERVICE_HUC_EDITOR_API_KEY
]  # Todo: This is encrypted in the .secrets.toml

#Authorization Form: It doesn't matter what you type in the form, it won't work yet. But we'll get there.
#See: https://fastapi.tiangolo.com/tutorial/security/first-steps/
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if settings.DISABLE_AUTHENTICATION:
        return

    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


@asynccontextmanager
async def lifespan(application: FastAPI):
    print('start up')
    print(emoji.emojize(':thumbs_up:'))


app = FastAPI(title=settings.FASTAPI_TITLE, description=settings.FASTAPI_DESCRIPTION,
              version=__version__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    public.router,
    tags=["Public"],
    prefix=""
)

app.include_router(
    protected.router,
    tags=["Protected"],
    prefix="",
    dependencies=[Depends(api_key_auth)]
)

if __name__ == "__main__":
    logging.info("Start")
    print(emoji.emojize(':thumbs_up:'))

    uvicorn.run("src.main:app", host="0.0.0.0", port=12104, reload=False)
