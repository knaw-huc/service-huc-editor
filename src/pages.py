"""
All endpoints which return HTML pages.
"""
import json
import logging
import os
from typing import Optional

from fastapi import Depends, HTTPException, APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.auth.authentication import def_user
from src.auth.authentication import get_user_with_app, allowed
from src.auth.models import User
from src.commons import settings
from src.config.dependencies import ConfigDep, ProfileDep
from src.records.records import rec_history
from src.xslt import StylesheetProcessor, StylesheetDep

router = APIRouter(
    prefix="/app/{app}",
)

@router.get('/profile/{prof}/record/{nr}/editor')
def get_editor(app: str, config: ConfigDep, prof: str, nr: str,
               stylesheet: StylesheetProcessor = Depends(StylesheetDep("editor"))):
    """
    Get the editor web page.
    :param app:
    :param config:
    :param prof:
    :param nr:
    :param stylesheet:
    :return:
    """
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] editor")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    stylesheet.set_parameter("cdn", settings.url_cdn)
    stylesheet.set_parameter("prof", prof)
    if nr:
        stylesheet.set_parameter("nr", nr)

    editor = stylesheet.apply()
    return HTMLResponse(content=editor)


@router.get('/profile/{prof}/record/editor')
def get_editor_new(app: str, config: ConfigDep, prof: str,
               stylesheet: StylesheetProcessor = Depends(StylesheetDep("editor"))):
    logging.info(f"app[{app}] prof[{prof}] new record editor")
    stylesheet.set_parameter("cdn", settings.url_cdn)
    stylesheet.set_parameter("prof", prof)

    editor = stylesheet.apply()
    return HTMLResponse(content=editor)

@router.get('/profile/{prof}/record/{nr}/history')
def get_history(request: Request, app: str, config: ConfigDep, nr: str,
                profile: ProfileDep,
                prof: str, user: Optional[User] = Depends(get_user_with_app),
                stylesheet: StylesheetProcessor = Depends(StylesheetDep("history2html"))):
    """
    Get the history of the record.
    :param profile:
    :param request:
    :param app:
    :param config:
    :param nr:
    :param prof:
    :param user:
    :param stylesheet:
    :return:
    """
    prof = profile['prof']
    if "text/html" in request.headers.get("accept", ""):
        stylesheet.set_parameter("nr", nr)
        stylesheet.set_parameter("prof", prof)
        result = stylesheet.main()
        return HTMLResponse(content=result)
    if not allowed(user, app, 'read', 'any', prof, nr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!",
                            headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] history")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    history = rec_history(app, prof, nr)
    return history


@router.get("")
async def get_app(request: Request, app: str,
                  stylesheet: StylesheetProcessor = Depends(StylesheetDep('listrecs'))):
    """
    Endpoint to read an application based on its name.
    This endpoint accepts the application name as a path parameter.
    If the application does not exist, it returns a 404 error.
    If the application exists but the reading functionality is not implemented yet, it returns a
    501 error.
    """
    logging.info(f"app[{app}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{app} doesn't exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logging.debug(f"app[{app}] accept[{request.headers["Accept"]}]")
    if "text/html" in request.headers.get("accept", ""):
        result = stylesheet.apply()
        return HTMLResponse(content=result)

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
