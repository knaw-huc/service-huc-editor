import logging
import os.path
import shutil


from fastapi import APIRouter, HTTPException, Request, Response
from starlette import status
from starlette.responses import JSONResponse

from src.commons import data, settings, get_profile_from_clarin

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




@router.delete("/profile/{id}")
async def delete_profile(request: Request, id: str):
    logging.info(f"Deleting profile {id}")
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}")
    return {"message": f"Profile {id} deleted"}


@router.put("/profile/{id}/tweak")
async def modify_profile_tweak(request: Request, id: str):
    logging.info(f"Modifying profile {id}")
    tweak_dir = f"{settings.URL_DATA_PROFILES}/{id}/tweak"
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        logging.debug(f"profile {id} doesn't exists")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.exists(tweak_dir):
        logging.debug(f"{tweak_dir} doesn't exists")
        os.makedirs(tweak_dir)
    if request.headers['Content-Type'] != 'application/xml':
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml")

    tweak_body = await request.body()

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/profile/{id}/tweak/{tweak_id}")
async def create_profile_tweak(request: Request, id: str, tweak_id: str):
    logging.info(f"Creating profile {id} tweak {tweak_id}")
    if not os.path.exists(f"{settings.URL_DATA_PROFILES}/{id}/tweak"):
        logging.debug(f"{settings.URL_DATA_PROFILES}/{id}/tweak doesn't exists")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/profile/{id}/tweak/{tweak_id}")
async def delete_profile_tweak(request: Request, id: str, tweak_id: str):
    logging.info(f"Deleting profile {id} tweak {tweak_id}")
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}/{tweak_id}"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}/{tweak_id}")

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
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}")
    return {"message": f"Record {id} deleted"}


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
    if not os.path.isdir(f"{settings.URL_DATA_PROFILES}/{id}/{resource_id}"):
        logging.info("Not found")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    shutil.rmtree(f"{settings.URL_DATA_PROFILES}/{id}/{resource_id}")

    return {"message": f"Resource {resource_id} deleted"}
