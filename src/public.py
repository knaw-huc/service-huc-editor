import logging
import os
import json
import pathlib

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from saxonche import PySaxonProcessor, PyXdmValue, PySaxonApiError


from src.commons import data, settings, tweak_nr

router = APIRouter()


@router.get('/info')
def info():
    """
    Endpoint to get the information about the HuC Editor API Service.
    This endpoint does not require any parameters and returns a JSON object containing the name and version of the service.
    """
    logging.info("HuC Editor API Service")
    logging.debug("info")
    return {"name": "HuC Editor API Service", "version": data["service-version"]}


@router.get('/profile/{id}')
def get_profile(request: Request, id: str):
    """
    Endpoint to get a profile based on its ID.
    This endpoint accepts the ID as a path parameter and the 'Accept' header to determine the response format.
    If the profile does not exist, it returns a 404 error.
    If the 'Accept' header is 'application/xml', it returns the profile data in XML format.
    If the 'Accept' header is 'application/json', it returns a 501 error as this functionality is not implemented yet.
    If the 'Accept' header is not 'application/xml' or 'application/json', it returns a 400 error.
    """
    logging.info(f"profile[{id}]")
    profile_path = f"{settings.URL_DATA_PROFILES}/{id}"
    if not os.path.isdir(profile_path):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with open(os.path.join(profile_path, f'{id}.xml'), 'r') as file:
        # Reading data from the xml file
        prof = file.read()

        tweaks = [t for t in pathlib.Path(f"{profile_path}/tweaks/").glob("tweak-*.xml")]
        tweaks.sort(key=tweak_nr)
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/mergeTweak.xsl")
            for tf in tweaks:
                with open(tf, 'r') as file:
                    logging.info(f"profile[{id}] apply tweak[{tf}]")
                    executable.set_parameter("tweakFile", proc.make_string_value(str(tf)))
                    pnode = proc.parse_xml(xml_text=prof)
                    prof = executable.transform_to_string(xdm_node=pnode)

        if request.headers["Accept"] == "application/xml":
            return Response(content=prof, media_type="application/xml")
        elif request.headers["Accept"] == "application/json":
            
            with PySaxonProcessor(license=False) as proc:
                xsltproc = proc.new_xslt30_processor()
                xsltproc.set_cwd(os.getcwd())
                executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/prof2json.xsl")
                node = proc.parse_xml(xml_text=prof)
                result = executable.transform_to_string(xdm_node=node)
                return JSONResponse(content=jsonable_encoder(json.loads(result)))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")


@router.get('/profile/{prof}/tweak/{nr}')
def get_profile_tweak(prof: str, nr: str):
    """
    Endpoint to get a tweak of a profile based on its ID.
    This endpoint accepts the ID as a path parameter.
    If the profile does not exist, it returns a 404 error.
    If the profile exists but the tweak is not implemented yet, it returns a 501 error.
    """
    logging.info(f"profile[{prof}] tweak[{nr}]")
    tweak_file = f"{settings.URL_DATA_PROFILES}/{id}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.debug(f"{tweak_file} doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with open(tweak_file, 'r') as file:
        tweak = file.read()
        return Response(content=tweak, media_type="application/xml")


@router.get("/{app_name}")
async def read_app(app_name: str):
    """
    Endpoint to read an application based on its name.
    This endpoint accepts the application name as a path parameter.
    If the application does not exist, it returns a 404 error.
    If the application exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"app[{app}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app_name}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{app_name} doesn't exists")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

@router.get('/{app}/record/{nr}')
def get_record(app: str, nr: str):
    """
    Endpoint to get a record based on its ID and the application name.
    This endpoint accepts the application name and the ID as path parameters.
    If the record does not exist, it returns a 404 error.
    If the record exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"app[{app}] record[{nr}]")
        record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"

    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with open(record_file, 'r') as file:
        rec = file.read()
        return Response(content=rec, media_type="application/xml")


@router.get('/{app_name}/record/{id}/resource/{resource_id}')
def get_record_resource(app_name: str, id: str, resource_id: str):
    """
    Endpoint to get a resource of a record based on its ID, the application name, and the resource ID.
    This endpoint accepts the application name, the record ID, and the resource ID as path parameters.
    If the resource does not exist, it returns a 404 error.
    If the resource exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"record {id} resource {resource_id}")
    if not os.path.exists(f"{settings.URL_DATA_PROFILES}/{app_name}/record/{id}/resource/{resource_id}"):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get('/cdn/huc-editor/{version}')
def get_cdn(version: str):
    """
    Endpoint to get the CDN (Content Delivery Network) for the HuC Editor based on its version.
    This endpoint accepts the version as a path parameter.
    Currently, this functionality is not implemented and returns a 501 error.
    """
    logging.info(f"cdn huc-editor {version}")
    # TODO: Waiting for Rob Zeeman's work.
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)