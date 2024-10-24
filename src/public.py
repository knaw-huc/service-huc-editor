import logging
import os
import json
import pathlib
from typing import Optional

import toml
import requests

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse, Response, RedirectResponse
from fastapi.encoders import jsonable_encoder
from enum import Enum
from weasyprint import HTML

from saxonche import PySaxonProcessor, PyXdmValue, PySaxonApiError

from src.commons import data, settings, tweak_nr

router = APIRouter()

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic(auto_error=False)

def get_current_user(credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    if not credentials:
        logging.debug("---no credentials---")
        return None

    correct_username = "guest"
    if credentials.username != correct_username:
        logging.debug("---no credentials---")
        return None

    return credentials.username

@router.get('/info')
def info(username: str = Depends(get_current_user)):

    """
    Endpoint to get the information about the HuC Editor API Service.
    This endpoint does not require any parameters and returns a JSON object containing the name and version of the service.
    """
    logging.info("HuC Editor API Service")
    logging.debug("info")
    return {"name": "HuC Editor API Service", "version": data["service-version"]}

@router.get('/proxy/skosmos/{inst}/home')
@router.get('/proxy/skosmos/{inst}/{vocab}/home')
def get_proxy(inst:str,vocab:str | None=None):
    logging.info(f"proxy skosmos[{inst}] vocab[{vocab}] home")
    proxy_file = f"{settings.proxies_dir}/skosmos-{inst}.toml"
    logging.info(f"proxy config[{proxy_file}]")
    if not os.path.isfile(proxy_file):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    with open(proxy_file, 'r') as f:
        proxy = toml.load(f)

        if vocab == None:
            vocab = proxy['base']['default']

        url=f"{proxy['base']['url']}/{vocab}/en/"
        return RedirectResponse(url=url)
        

@router.get('/proxy/skosmos/{inst}')
@router.get('/proxy/skosmos/{inst}/{vocab}')
def get_proxy(inst:str,vocab:str | None=None,q: str | None = "*"):
    logging.info(f"proxy skosmos[{inst}] vocab[{vocab}] q[{q}]")
    proxy_file = f"{settings.proxies_dir}/skosmos-{inst}.toml"
    logging.info(f"proxy config[{proxy_file}]")
    if not os.path.isfile(proxy_file):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    with open(proxy_file, 'r') as f:
        proxy = toml.load(f)

        if vocab == None:
            vocab = proxy['base']['default']

        if q.startswith('^'):
            q = q.removeprefix('^') + "*"
        else:
            q = "*" + q + "*"

        logging.info(f"proxy skosmos[{inst}] vocab[{vocab}] q[{q}]")
        url=f"{proxy['base']['url']}/rest/v1/{vocab}/search"
        params = {'unique': 'yes','lang': 'en','query': q}

        r = requests.get(url, params=params)
        logging.info(f"proxy[{r.url}] [{r.text}]")

        js = json.loads(r.text)

        lbls = []
        for res in js['results']:
            lbls.append(res['prefLabel'])

        res = {'query':"unit", 'suggestions':lbls}
         
        return JSONResponse(jsonable_encoder(res))

def prof_xml(id:str):
    profile_path = f"{settings.URL_DATA_PROFILES}/{id}"
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
        return prof
    return None


def prof_json(id:str):
    prof = prof_xml(id)
    if (prof):
            with PySaxonProcessor(license=False) as proc:
                xsltproc = proc.new_xslt30_processor()
                xsltproc.set_cwd(os.getcwd())
                executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/prof2json.xsl")
                node = proc.parse_xml(xml_text=prof)
                return  executable.transform_to_string(xdm_node=node)
    return None


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
    
    if request.headers["Accept"] == "application/xml":
        prof = prof_xml(id)
        if (prof):
            return Response(content=prof, media_type="application/xml")
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    elif "application/json" in request.headers.get("accept", ""):
        prof = prof_json(id)
        if (prof):
            return JSONResponse(content=jsonable_encoder(json.loads(prof)))
        else:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")


@router.get('/profile/{prof}/tweak/{nr}')
def get_profile_tweak(request: Request, prof: str, nr: str):
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


@router.get("/app/{app}")
async def read_app(request: Request, app: str):
    """
    Endpoint to read an application based on its name.
    This endpoint accepts the application name as a path parameter.
    If the application does not exist, it returns a 404 error.
    If the application exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"app[{app}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{app} doesn't exist!")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logging.debug(f"app[{app}] accept[{request.headers["Accept"]}]")
    if "text/html" in request.headers.get("accept", ""):
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/listrecs.xsl")
            executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
            executable.set_parameter("base", proc.make_string_value(settings.url_base))
            config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
            executable.set_parameter("app", proc.make_string_value(app))
            null = proc.parse_xml(xml_text="<null/>")
            result = executable.transform_to_string(xdm_node=null)
            return HTMLResponse(content=result)
            
    return HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)

def rec_html(app,nr):
    record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"
    with open(record_file, 'r') as file:
        rec = file.read()
        with PySaxonProcessor(license=False) as proc:
            rec = proc.parse_xml(xml_text=rec)
            xpproc = proc.new_xpath_processor()
            xpproc.set_cwd(os.getcwd())
            xpproc.declare_namespace('clariah','http://www.clariah.eu/')
            xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')
            xpproc.set_context(xdm_item=rec)
            prof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
            prof = prof_xml(prof)
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/toHTML.xsl")
            executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
            executable.set_parameter("base", proc.make_string_value(settings.url_base))
            executable.set_parameter("app", proc.make_string_value(app))
            executable.set_parameter("nr", proc.make_string_value(nr))
            prof = proc.parse_xml(xml_text=prof)
            executable.set_parameter("tweak-doc",prof) 
            config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
            executable.set_parameter("config", config)
            return executable.transform_to_string(xdm_node=rec)

def rec_editor(app,nr):
    if nr:
        logging.info(f"app[{app}] record[{nr}] editor")
    else:
        logging.info(f"app[{app}] new record editor")
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/editor.xsl")
        executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
        executable.set_parameter("base", proc.make_string_value(settings.url_base))
        executable.set_parameter("app", proc.make_string_value(app))
        if nr:
            executable.set_parameter("nr", proc.make_string_value(nr))
        config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
        executable.set_parameter("config", config)
        null = proc.parse_xml(xml_text="<null/>")
        return executable.transform_to_string(xdm_node=null)

@router.get('/app/{app}/record/editor')
@router.get('/app/{app}/record/{nr}/editor')
def get_editor(request: Request, app: str, nr: str | None=None):
    if nr:
        logging.info(f"app[{app}] record[{nr}] editor")
        record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"
        if not os.path.exists(record_file):
            logging.debug(f"{record_file} doesn't exist")
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        logging.info(f"app[{app}] new record editor")        
    
    if "text/html" in request.headers.get("accept", ""):
        editor = rec_editor(app,nr)
        return HTMLResponse(content=editor)

class RecForm(str, Enum):
    json = "json"
    xml = "xml"
    html = "html"
    pdf = "pdf"

@router.get('/app/{app}/record/{nr}')
def get_record(request: Request, app: str, nr: str ):
    if nr.count('.') == 0:
        form = "html"
    elif nr.count('.') == 1:
        nr, form = nr.rsplit('.', 1)
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

    if form not in ["json", "xml", "html", "pdf"]:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")
    """
    Endpoint to get a record based on its ID and the application name.
    This endpoint accepts the application name and the ID as path parameters.
    If the record does not exist, it returns a 404 error.
    If the record exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    #?is er iemand ingelogd of is er een gast?
    logging.info(f"app[{app}] record[{nr}] form[{form}] accept[{request.headers.get("accept", "")}]")
    record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"

    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if form == "json" or "application/json" in request.headers.get("accept", ""):
        with PySaxonProcessor(license=False) as proc:
            rec = proc.parse_xml(xml_file_name=record_file)
            xpproc = proc.new_xpath_processor()
            xpproc.set_cwd(os.getcwd())
            xpproc.declare_namespace('clariah','http://www.clariah.eu/')
            xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')
            xpproc.set_context(xdm_item=rec)
            prof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
            prof_doc = prof_json(prof)
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/rec2json.xsl")
            executable.set_parameter("prof-doc", proc.make_string_value(prof_doc))
            executable.set_parameter("rec-nr", proc.make_string_value(nr))
            result = executable.transform_to_string(xdm_node=rec)
            return JSONResponse(content=jsonable_encoder(json.loads(result)))
    elif form == RecForm.pdf or "application/pdf" in request.headers.get("accept", ""):
            html = rec_html(app,nr)
            pdf = HTML(string=html).write_pdf()
            headers = {'Content-Disposition': f'inline; filename="{app}-record-{nr}.pdf"'}
            return Response(pdf, headers=headers, media_type='application/pdf')
    # FF sends an Accept header with text/html and application/xml, we prefer html, 
    # but first check for an explicit xml request
    elif form == RecForm.xml:
        with open(record_file, 'r') as file:
            rec = file.read()
            return Response(content=rec, media_type="application/xml")
    elif form == RecForm.html or "text/html" in request.headers.get("accept", ""):
            html = rec_html(app,nr)
            return HTMLResponse(content=html)
    elif form == RecForm.xml or "application/xml" in request.headers.get("accept", ""):
        with open(record_file, 'r') as file:
            rec = file.read()
            return Response(content=rec, media_type="application/xml")

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

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