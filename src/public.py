import logging
import os
import json
import urllib.parse
import toml
import requests
import urllib

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse

from saxonche import PySaxonProcessor

from src.commons import data, settings
from src.profiles import prof_xml, prof_json

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

@router.get('/proxy/nominatim/{inst}')
def get_proxy_nominatim(inst:str,q: str | None = None):
    logging.info(f"proxy nominatim[{inst}] vq[{q}]")
    proxy_file = f"{settings.proxies_dir}/nominatim-{inst}.toml"
    logging.info(f"proxy config[{proxy_file}]")
    if not os.path.isfile(proxy_file):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    entries = []

    if q != None or q.strip() !='':
    
        with open(proxy_file, 'r') as f:
            proxy = toml.load(f)

            #url=f"{proxy['base']['url']}/search.php"
            #params = {'q': q}
            url=f"{proxy['base']['url']}/search.php?{urllib.parse.urlencode({'q': q})}"
            logging.info(f"proxy[{url}]")

            r = requests.get(url)
            #r = requests.get(url, params=params)
            #http://nominatim:8080/search.php?q=Jardin+Exotique%2C+Monaco
            #r = requests.get('http://host.docker.internal:1311/search.php?q=Jardin+Exotique%2C+Monaco')
            #http://host.docker.internal:1311/search.php?q=Jardin%20Exotique%2C%20Monaco
            logging.info(f"proxy[{r.url}]=>[{r.text}]")

            js = json.loads(r.text)

            for res in js:
                data = {'label': res['display_name'],'uri': f" https://www.openstreetmap.org/{res['osm_type']}/{res['osm_id']}"}
                entry = {'value': data['label'],'data': data}
                entries.append(entry)

        res = {'query':"unit", 'suggestions':entries}
         
        return JSONResponse(jsonable_encoder(res))


@router.get('/proxy/skosmos/{inst}/index')
@router.get('/proxy/skosmos/{inst}/{vocab}/index')
def get_proxy_skosmos_index(inst:str,vocab:str | None=None):
    logging.info(f"proxy skosmos[{inst}] vocab[{vocab}] index")
    proxy_file = f"{settings.proxies_dir}/skosmos-{inst}.toml"
    logging.info(f"proxy config[{proxy_file}]")
    if not os.path.isfile(proxy_file):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    with open(proxy_file, 'r') as f:
        proxy = toml.load(f)

        if vocab == None:
            vocab = proxy['base']['default']

        url=f"{proxy['base']['url']}/rest/v1/{vocab}/index/"
        r = requests.get(url)
        logging.info(f"proxy[{r.url}] [{r.text}]")

        js = json.loads(r.text)
        res = {'index': ''.join(js['indexLetters'])}
        logging.info(f"proxy[{r.url}] [{r.text}] index[{res}]")

        return JSONResponse(jsonable_encoder(res))
        

@router.get('/proxy/skosmos/{inst}/home')
@router.get('/proxy/skosmos/{inst}/{vocab}/home')
def get_proxy_skosmos_home(inst:str,vocab:str | None=None):
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
def get_proxy_skosmos(inst:str,vocab:str | None=None,q: str | None = "*"):
    logging.info(f"proxy skosmos[{inst}] vocab[{vocab}] q[{q}]")
    proxy_file = f"{settings.proxies_dir}/skosmos-{inst}.toml"
    logging.info(f"proxy config[{proxy_file}]")
    if not os.path.isfile(proxy_file):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
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

        entries = []
        for res in js['results']:
            data = {'label': res['prefLabel'],'uri': res['uri']}
            entry = {'value': data['label'],'data': data}
            entries.append(entry)

        res = {'query':"unit", 'suggestions':entries}
         
        return JSONResponse(jsonable_encoder(res))

@router.get('/app/{app}/profile/{id}')
def get_profile(request: Request, app: str, id: str):
    """
    Endpoint to get a profile based on its ID.
    This endpoint accepts the ID as a path parameter and the 'Accept' header to determine the response format.
    If the profile does not exist, it returns a 404 error.
    If the 'Accept' header is 'application/xml', it returns the profile data in XML format.
    If the 'Accept' header is 'application/json', it returns a 501 error as this functionality is not implemented yet.
    If the 'Accept' header is not 'application/xml' or 'application/json', it returns a 400 error.
    """

    form="xml"
    if id.endswith(".xml"):
        form = "xml"
        id = id.removesuffix(".xml")
    if id.endswith(".json"):
        form = "json"
        id = id.removesuffix(".json")
    if form not in ["xml", "json"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported 2")
    logging.info(f"app[{app}] profile[{id}] form[{form}]")
    profile_path = f"{settings.URL_DATA_APPS}/{app}/profiles/{id}"
    if not os.path.isdir(profile_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if form == "json" or "application/json" in request.headers.get("accept", ""):
        prof = prof_json(app, id)
        if (prof):
            return JSONResponse(content=jsonable_encoder(json.loads(prof)))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    elif form == "xml" or "application/xml" in request.headers.get("accept", ""):
        prof = prof_xml(app, id)
        if (prof):
            return Response(content=prof, media_type="application/xml")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported 3")

@router.get('/app/{app}/profile/{prof}/tweak/template')
def get_profile_tweak_template(request: Request, app: str, prof: str):
    logging.info(f"app[{app}] profile[{prof}] tweak template")
    profile_path = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}"
    if not os.path.isdir(profile_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)    
    with PySaxonProcessor(license=False) as proc:
        prof = proc.parse_xml(xml_file_name=f"{profile_path}/{prof}.xml")
        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/toTweak.xsl")
        template = executable.transform_to_string(xdm_node=prof)
        return Response(content=template, media_type="application/xml")

@router.get('/app/{app}/profile/{prof}/tweak/{nr}')
def get_profile_tweak(request: Request, app: str, prof: str, nr: str):
    """
    Endpoint to get a tweak of a profile based on its ID.
    This endpoint accepts the ID as a path parameter.
    If the profile does not exist, it returns a 404 error.
    If the profile exists but the tweak is not implemented yet, it returns a 501 error.
    """
    logging.info(f"profile[{prof}] tweak[{nr}]")
    tweak_file =f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.debug(f"{tweak_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with open(tweak_file, 'r') as file:
        tweak = file.read()
        return Response(content=tweak, media_type="application/xml")