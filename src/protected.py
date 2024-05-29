import logging
from urllib import request

from fastapi import APIRouter, HTTPException, Request
from starlette import status

from src.commons import data

router = APIRouter()


@router.post("/profile/{id}")
async def create_profile(request: Request, id: str):
    logging.info(f"Creating profile {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

@router.delete("/profile/{id}")
async def delete_profile(request: Request, id: str):
    logging.info(f"Deleting profile {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/profile/{id}/tweak")
async def modify_profile_tweak(request: Request, id: str):
    logging.info(f"Modifying profile {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/profile/{id}/tweak/{tweak_id}")
async def create_profile_tweak(request: Request, id: str, tweak_id: str):
    logging.info(f"Creating profile tweak {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/profile/{id}/tweak/{tweak_id}")
async def delete_profile_tweak(request: Request, id: str, tweak_id: str):
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/record")
async def modify_record(request: Request):
    logging.info(f"Modifying record")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/record/{id}")
async def create_record(request: Request, id: str):
    logging.info(f"Creating record {id}")

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/record/{id}")
async def delete_record(request: Request, id: str):
    logging.info(f"Deleting record {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/record/{id}/resource")
async def create_record_resource(request: Request, id: str):
    logging.info(f"Creating record resource {id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/record/{id}/resource/{resource_id}")
async def create_record_resource(request: Request, id: str, resource_id: str):
    logging.info(f"Creating record {id} resource {resource_id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/record/{id}/resource/{resource_id}")
async def delete_record_resource(request: Request, id: str, resource_id: str):
    logging.info(f"Deleting record {id} resource {resource_id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)