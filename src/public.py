import logging

from fastapi import APIRouter, HTTPException
from starlette import status

from src.commons import data

router = APIRouter()


@router.get('/info')
def info():
    logging.info("HuC Editor API Service")
    logging.debug("info")
    return {"name": "HuC Editor API Service", "version": data["service-version"]}


@router.get('/profile/{id}')
def get_profile(id: str):
    logging.info(f"profile {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

@router.get('/profile/{id}/tweak')
def get_profile_tweak(id: str):
    logging.info(f"profile tweak id: {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/record/{id}')
def get_record(id: str):
    logging.info(f"record {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/record/{id}/resource/{resource_id}')
def get_record_resource(id: str, resource_id: str):
    logging.info(f"record {id} resource {resource_id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/cdn/huc-editor/{version}')
def get_cdn(version: str):
    logging.info(f"cdn huc-editor {version}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)