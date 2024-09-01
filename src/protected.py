import logging
import os.path
import shutil
import uuid

from fastapi import APIRouter, HTTPException, Request, Response
from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from src.commons import data, settings, get_profile_from_clarin

router = APIRouter()

# example id: clarin.eu:cr1:p_1653377925727
@router.put("/profile/{id}", status_code=status.HTTP_201_CREATED)
async def create_profile(id: str):
    """
    Endpoint to create a profile based on its ID.
    If the profile already exists, it returns a message indicating that the profile already exists.
    """
    logging.info(f"Creating profile {id}")
    profile_path = f"{settings.URL_DATA_PROFILES}/{id}"
    profile_xml = await get_profile_from_clarin(id)
    if not os.path.isdir(profile_path):
        os.makedirs(profile_path)

        with open(os.path.join(profile_path, f'{id}.xml'), 'wb') as file:
            file.write(profile_xml)
        return {"message": f"Profile[{id}] is created"}
    else:
        with open(os.path.join(profile_path, f'{id}.xml'), 'wb') as file:
            file.write(profile_xml)
        return JSONResponse({"message": f"Profile[{id}] is refreshed"}, status_code=status.HTTP_200_OK)


@router.delete("/profile/{id}")
async def delete_profile(request: Request, id: str):
    """
    Endpoint to mark a profile as deleted based on its ID.
    """
    logging.info(f"Deleting profile[{id}]")
    
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}.deleted"):
        shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}.deleted")

    shutil.move(f"{settings.URL_DATA_PROFILES}/{id}", f"{settings.URL_DATA_PROFILES}/{clarin_id}.deleted")

    return {"message": f"Profile[{id}] is marked as deleted"}

@router.post("/profile/{id}/tweak", status_code=status.HTTP_201_CREATED)
async def create_profile_tweak(request: Request, id: str):
    """
    Endpoint to create a profile tweak.
    If the profile does not exist, it returns a 404 error.
    """
    logging.info(f"Modifying profile[{id}]")
    tweak_dir = f"{settings.URL_DATA_PROFILES}/{id}/tweaks"
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        logging.debug(f"profile[{id}] doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.exists(tweak_dir):
        logging.debug(f"{tweak_dir} doesn't exist")
        os.makedirs(tweak_dir)
    nr = 1
    tweak_file = f"{tweak_dir}/tweak-{nr}.xml"
    while os.path.exists(tweak_file):
        nr = nr + 1
        tweak_file = f"{tweak_dir}/tweak-{nr}.xml"
    if request.headers['Content-Type'] != 'application/xml':
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml")

    tweak_body = await request.body()
    with open(tweak_file, 'wb') as file:
        file.write(tweak_body)
    return RedirectResponse(url=f"./{nr}") 

@router.put("/profile/{id}/tweak/{nr}")
async def modify_profile_tweak(request: Request, id: str, nr: str):
    """
    Endpoint to modify a profile tweak based on its ID and tweak NR.
    If the profile or tweak does not exist, it returns a 404 error.
    """
    logging.info(f"Modifying profile[{id}] tweak{nr}")
    tweak_file = f"{settings.URL_DATA_PROFILES}/{id}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.debug(f"{tweak_file} doesn't exists")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if request.headers['Content-Type'] != 'application/xml':
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml")

    tweak_body = await request.body()
    with open(tweak_file, 'wb') as file:
        file.write(tweak_body)

    return JSONResponse({"message": f"Profile[{id}] tweak[{nr}] modified"})

@router.delete("/profile/{id}/tweak/{nr}")
async def delete_profile_tweak(request: Request, id: str, nr: str):
    """
    Endpoint to delete a profile tweak based on its ID and tweak NR.
    If the profile tweak does not exist, it returns a 404 error.
    """
    logging.info(f"Deleting profile[{id}] tweak[{nr}]")
    tweak_file = f"{settings.URL_DATA_PROFILES}/{id}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.info(f"{tweak_file} not found!")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.exists(f"{tweak_file}.deleted"):
        os.remove(f"{tweak_file}.deleted")
    os.rename(tweak_file,f"{tweak_file}.deleted")

    return JSONResponse({"message": f"Profile[{id}] tweak[{nr}] deleted"})


@router.put("/app/{app}", status_code=status.HTTP_201_CREATED)
async def create_app(app: str):
    """
    Endpoint to create an application based on its name.
    If the application already exists, it returns a message indicating that the application already exists.
    """
    logging.info(f"Creating app[{app}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{app} doesn't exists")
        os.makedirs(f"{settings.URL_DATA_APPS}/{app}")
        return JSONResponse({"message": f"App[{app}] is created"}, status_code=status.HTTP_201_CREATED)

    return JSONResponse({"message": f"App[{app}] already exist."}, status_code=status.HTTP_200_OK)


@router.post("/app/{app}/record", status_code=status.HTTP_201_CREATED)
async def create_record(request: Request, app: str):
    """
    Endpoint to create a record for an application.
    If the app does not exist, it returns a 400 error.
    """
    logging.info(f"Modifying app[{app}]")
    record_dir = f"{settings.URL_DATA_APPS}/{app}/records"
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"app[{app}] doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.exists(record_dir):
        logging.debug(f"{record_dir} doesn't exist")
        os.makedirs(record_dir)

    nr = 1
    record_file = f"{record_dir}/record-{nr}.xml"
    while os.path.exists(record_file) or os.path.exists(f"{record_file}.deleted"):
        nr = nr + 1
        record_file = f"{record_dir}/record-{nr}.xml"

    if request.headers['Content-Type'] != 'application/xml' and request.headers['Content-Type'] != 'application/json':
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml or application/json")

    record_body = await request.body()


    if request.headers['Content-Type'] == 'application/json':
        # TODO: conversion json -> xml
        foobar

    with open(record_file, 'wb') as file:
        file.write(record_body)
    return RedirectResponse(url=f"./{nr}") 

@router.post("/app/{app}/record/{nr}")
async def modify_record(request: Request, app: str, nr: str):
    """
    Endpoint to create a record for an application based on its name and the record's ID.
    If the record already exists, it returns a message indicating that the record already exists.
    """
    logging.info(f"Modifying app[{app}] record[{nr}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app_name}/record/{id}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{id}/record doesn't exists")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # TODO: Waiting for Menzo's xslt implementation

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/record/{id}")
async def delete_record(request: Request, id: str):
    """
    Endpoint to delete a record based on its ID.
    If the record does not exist, it returns a 404 error.
    """
    logging.info(f"Deleting record {id}")
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}")
    return {"message": f"Record {id} deleted"}


@router.put("{app_name}/record/{id}/resource")
async def create_record_resource(request: Request, app_name: str, id: str):
    """
    Endpoint to create a resource for a record of an application based on the application's name, the record's ID.
    If the resource already exists, it returns a message indicating that the resource already exists.
    """
    logging.info(f"Creating record resource {id}")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app_name}/record/{id}/resource"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/record/{id}/resource/{resource_id}")
async def create_record_resource(request: Request, id: str, resource_id: str):
    """
    Endpoint to create a resource for a record based on the record's ID and the resource's ID.
    If the resource already exists, it returns a message indicating that the resource already exists.
    """
    logging.info(f"Creating record {id} resource {resource_id}")
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/record/{id}/resource/{resource_id}")
async def delete_record_resource(request: Request, id: str, resource_id: str):
    """
    Endpoint to delete a resource of a record based on the record's ID and the resource's ID.
    If the resource does not exist, it returns a 404 error.
    """
    logging.info(f"Deleting record {id} resource {resource_id}")
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}/{resource_id}"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}/{resource_id}")

    return {"message": f"Resource {resource_id} deleted"}
