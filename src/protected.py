import logging
import os.path

import requests as req

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.openapi.models import Response
from starlette import status
from starlette.responses import JSONResponse

from src.commons import data, settings

router = APIRouter()


# example id: clarin.eu:cr1:p_1653377925727
@router.post("/profile/{id}", status_code=status.HTTP_201_CREATED)
async def create_profile(id: str):
    logging.info(f"Creating profile {id}")
    # TODO: don't use hard coded e.g. split(":")[2]
    clarin_id = id.rsplit(':', 1)[-1]
    profile_path = f"{settings.URL_DATA_PROFILES}/{clarin_id}"
    if not os.path.isdir(profile_path):
        logging.debug(f"{profile_path} doesn't exists")
        os.makedirs(profile_path)
        profile_xml = await get_profile_from_clarin(id)

        with open(os.path.join(profile_path, f'{clarin_id}.xml'), 'wb') as file:
            file.write(profile_xml)
        return {"message": "Profile is created"}
    else:
        print(f"{profile_path} exists")
        return JSONResponse({"message": "Profile already exists"}, status_code=status.HTTP_200_OK)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


async def get_profile_from_clarin(id):
    clarin_url = settings.URL_CLARIN_COMPONENT_REGISTRY % id
    logging.debug(f"{clarin_url}")
    clarin_profile = req.get(clarin_url)
    if clarin_profile.status_code != status.HTTP_200_OK:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return clarin_profile.content


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
