import logging
import os

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request

from src.commons import data, settings

router = APIRouter()


@router.get('/info')
def info():
    logging.info("HuC Editor API Service")
    logging.debug("info")
    return {"name": "HuC Editor API Service", "version": data["service-version"]}


@router.get('/profile/{id}')
def get_profile(request: Request, id: str):
    logging.info(f"profile {id}")
    clarin_id = id.rsplit(':', 1)[-1]
    profile_path = f"{settings.URL_DATA_PROFILES}/{clarin_id}"
    if not os.path.isdir(profile_path):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if request.headers["Accept"] == "application/xml":
        # Reading data from the xml file
        with open(os.path.join(profile_path, f'{clarin_id}.xml'), 'r') as file:
            return file.read()
    elif request.headers["Accept"] == "application/json":
        return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")


@router.get('/profile/{id}/tweak')
def get_profile_tweak(id: str):
    logging.info(f"profile tweak id: {id}")
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/record/{id}')
def get_record(id: str):
    logging.info(f"record {id}")
    if not os.path.exists(f"{settings.URL_DATA_PROFILES}/{id}.json"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/record/{id}/resource/{resource_id}')
def get_record_resource(id: str, resource_id: str):
    logging.info(f"record {id} resource {resource_id}")
    if not os.path.exists(f"{settings.URL_DATA_PROFILES}/{id}/{resource_id}.json"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/cdn/huc-editor/{version}')
def get_cdn(version: str):
    logging.info(f"cdn huc-editor {version}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
