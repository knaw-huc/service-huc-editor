import os

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from typing import Annotated

from sqlmodel import SQLModel, Session, select

from src.auth.authentication import initialize_users
from src.auth.authentication import create_user
from src.auth.models import User
from src.config.dependencies import get_all_apps, get_app_configuration
from src.database import get_db_eng_for_app
from src.commons import api_keys
import logging
from contextlib import asynccontextmanager

import emoji
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, status

from src.commons import settings

__version__ = "0.1.10"

from starlette.middleware.cors import CORSMiddleware

from src import public, protected, admin
from src.auth.routes import router as auth_router

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

    print("Available apps:")

    for a in get_all_apps():
        print(f" - {a}")
        eng = get_db_eng_for_app(a)
        config = get_app_configuration(a)
        SQLModel.metadata.create_all(eng)

        with Session(eng) as session:
            print("Check if this app has users")
            initialize_users(a, config, session)

    yield


app = FastAPI(title=settings.FASTAPI_TITLE, description=settings.FASTAPI_DESCRIPTION,
              version=__version__, lifespan=lifespan)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
for root, dirs, files in os.walk(settings.URL_DATA_APPS):
    if 'static' in dirs:
        static_path = os.path.join(root, 'static')
        static_path_app = os.path.basename(root)
        if static_path_app == 'resources':
            static_path_app = os.path.basename(os.path.abspath(os.path.join(root, os.pardir)))
        logging.info(f"Found 'static' directory at: {static_path} for {static_path_app}")
        app.mount(f"/app/{static_path_app}/static", StaticFiles(directory=static_path), name="static")
        logging.info(f"Mounted {static_path_app} static directory at: {static_path}")

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

app.include_router(
    auth_router
)

if __name__ == "__main__":
    logging.info("Start")
    print(emoji.emojize(':thumbs_up:'))

    uvicorn.run("src.main:app", host="0.0.0.0", port=1210, reload=False, forwarded_allow_ips='*',workers=4)
