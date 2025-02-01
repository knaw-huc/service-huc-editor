import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import emoji
import importlib.metadata
from src.commons import settings, data
import importlib.metadata
import logging
from contextlib import asynccontextmanager

import emoji
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, status

from src.commons import settings, data

__version__ = importlib.metadata.metadata(settings.SERVICE_NAME)["version"]

from starlette.middleware.cors import CORSMiddleware

from src import public, protected, admin

api_keys = [
    settings.SERVICE_HUC_EDITOR_API_KEY
]  # Todo: This is encrypted in the .secrets.toml


security = HTTPBearer()


def auth_header(request: Request, auth_cred: Annotated[HTTPAuthorizationCredentials, Depends(security)]):

    if settings.DISABLE_AUTHENTICATION:
        return

    if not auth_cred or auth_cred.credentials not in api_keys:
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

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
for root, dirs, files in os.walk(settings.URL_DATA_APPS):
    if 'static' in dirs:
        static_path = os.path.join(root, 'static')
        logging.info(f"Found 'static' directory at: {static_path}")
        app.mount(f"/app/{os.path.basename(root)}/static", StaticFiles(directory=static_path), name="static")
        logging.info(f"Mounted {os.path.basename(root)} static directory at: {static_path}")

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
    admin.router,
    tags=["Admin"],
    prefix="",
    dependencies=[Depends(auth_header)]
)
app.include_router(
    protected.router,
    tags=["Protected"],
    prefix=""
)

if __name__ == "__main__":
    logging.info("Start")
    print(emoji.emojize(':thumbs_up:'))

    uvicorn.run("src.main:app", host="0.0.0.0", port=1210, reload=False)
