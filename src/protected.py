import logging
import os.path
import shutil
import json
import toml

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder

from passlib.apache import HtpasswdFile

from saxonche import PySaxonProcessor

from starlette import status
from starlette.responses import HTMLResponse,  JSONResponse, RedirectResponse

from weasyprint import HTML

from typing import Optional
from enum import Enum

from src.commons import settings, convert_toml_to_xml, call_record_create_hook, allowed
from src.records import rec_html, rec_editor, rec_update
from src.profiles import prof_json

router = APIRouter()

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic(auto_error=False)

def get_current_user(app: str, credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    if not credentials:
        logging.debug("---no credentials---")
        return None

    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(config_app_file):
        logging.error(f"config file {config_app_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App config file not found")

    users_cred_file = None
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        if 'access' in config["app"]:
            if 'users' in config['app']['access']:
                users_cred_file = config['app']['access']['users']
                users_cred_file = os.path.normpath(os.path.join(f"{settings.URL_DATA_APPS}/{app}/", users_cred_file))
                if not os.path.isfile(users_cred_file):
                    logging.error(f"users file {users_cred_file} doesn't exist")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users file not found")

    if users_cred_file:
        ht = HtpasswdFile(users_cred_file)
        valid_user = ht.check_password(credentials.username, credentials.password)
        if not valid_user:
            # valid_user = None means that the user is not valid
            # valid_user = False means that the user is valid but the password is incorrect
            logging.debug("---no credentials---")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})

    return credentials.username

def get_user_with_app(app: str, credentials: HTTPBasicCredentials = Depends(security)):
    return get_current_user(app, credentials)

@router.post("/app/{app}/record/", status_code=status.HTTP_201_CREATED)
@router.post("/app/{app}/profile/{prof}/record/", status_code=status.HTTP_201_CREATED)
async def create_record(request: Request, app: str, prof: str | None = None, redir: str | None = "yes", user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'write','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    config = None
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
    if (prof == None):
        prof = config['app']['def_prof'] 
    """
    Endpoint to create a record for an application.
    If the app does not exist, it returns a 400 error.
    """
    
    logging.info(f"Modifying app[{app}] prof[{prof}]: creating record")
    record_dir = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records"
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"app[{app}] doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}"):
        logging.debug(f"app[{app}] prof[{prof}] doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.exists(record_dir):
        logging.debug(f"{record_dir} doesn't exist")
        os.makedirs(record_dir)

    nr = 1
    record_file = f"{record_dir}/record-{nr}.xml"
    while os.path.exists(record_file) or os.path.exists(f"{record_file}.deleted"):
        nr = nr + 1
        record_file = f"{record_dir}/record-{nr}.xml"
    logging.info(f"app[{app}] record[{nr}] create")

    if not('application/xml' in request.headers['Content-Type'] or 'application/json' in request.headers['Content-Type']):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml or application/json!")
    
    record_body = await request.body()

    if 'application/json' in request.headers['Content-Type']:
        logging.info(f"record[{nr}] JSON to XML]")
        logging.info(f"- body JSON[{json.dumps(json.loads(record_body))}]")
        js = json.loads(record_body)
        rec = js
        if js["record"] != None:
            rec = js["record"]
        logging.info(f"- record JSON[{json.dumps(rec)}]")
        if prof != None and js["prof"] != None and prof != js["prof"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The profile in the path (or the app default) and the profile in the JSON differ! ({prof}!={js['prof']})")
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/json2rec.xsl")
            executable.set_parameter("js-doc", proc.make_string_value(json.dumps(rec)))
            if 'cmdi_version' in config["app"]:
                executable.set_parameter("vers", proc.make_string_value(config['app']['cmdi_version']))
            if (user == None):
                user = "server"
            executable.set_parameter("user", proc.make_string_value(user))
            executable.set_parameter("self", proc.make_string_value(f"unl://{nr}"))
            executable.set_parameter("prof", proc.make_string_value(prof.strip()))
            null = proc.parse_xml(xml_text="<null/>")
            record_body = executable.transform_to_string(xdm_node=null)
        with open(record_file, 'w') as file:
            file.write(record_body)
            config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
            with open(config_file, 'r') as f:
                config = toml.load(f)
                if "hooks" in config['app'] and "record" in config["app"]["hooks"] and "create" in config["app"]["hooks"]["record"]:
                    logging.info(f"call_record_create_hook(hook[{config['app']['hooks']['record']['create']}],app[{app}],rec[{nr}])")
                    call_record_create_hook(config['app']['hooks']['record']['create'],app,prof,nr)
    else:
        with open(record_file, 'wb') as file:
            file.write(record_body)
        err = rec_update(app, nr, record_body.decode())
        logging.info(f"update app[{app}] prof[{prof}] record[{nr}] msg[{err}]")
        if (err.strip() == "404"):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Initial record[{nr}] version was not saved!")
        elif (err.strip() != "OK"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        if redir.strip() != "no":
            return RedirectResponse(url=f"./{nr}")
    return JSONResponse({"message": f"App[{app}] prof[{prof}] record[{nr}] created","nr": nr})

@router.put("/app/{app}/record/{nr}")
@router.put("/app/{app}/profile/{prof}/record/{nr}")
async def modify_record(request: Request, app: str, nr: str, prof: str | None = None, when: str | None = None, user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'write','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    config=None
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
    if (prof == None):
        prof = config['app']['def_prof'] 
    """
    Endpoint to create a record for an application based on its name and the record's ID.
    If the record already exists, it returns a message indicating that the record already exists.
    """
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] modify")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not('application/xml' in request.headers['Content-Type'] or 'application/json' in request.headers['Content-Type']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml or application/json!")
    
    record_body = await request.body()

    if 'application/json' in request.headers['Content-Type']:
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/json2rec.xsl")
            logging.info(f"record[{nr}] JSON to XML]")
            logging.info(f"- body JSON[{record_body}]")
            js = json.loads(record_body)
            rec = js
            if js['record'] != None:
                rec = js['record']
            logging.info(f"- record JSON[{json.dumps(rec)}]")
            executable.set_parameter("js-doc", proc.make_string_value(json.dumps(rec)))
            if (user == None):
                user = "server"
            executable.set_parameter("user", proc.make_string_value(user))
            if 'cmdi_version' in config["app"]:
                executable.set_parameter("vers", proc.make_string_value(config['app']['cmdi_version']))
            executable.set_parameter("self", proc.make_string_value(f"unl://{nr}"))
            if prof != None and js["prof"] != None and prof != js["prof"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The profile in the path (or the app default) and the profile in the JSON differ! ({prof}!={js['prof']})")
            executable.set_parameter("prof", proc.make_string_value(prof.strip()))
            if (when==None):
                if (js['when']!=None):
                    when = js['when']
                else:
                    old = proc.parse_xml(xml_file_name=record_file)
                    xpproc = proc.new_xpath_processor()
                    xpproc.set_cwd(os.getcwd())
                    xpproc.set_context(xdm_item=old)
                    when = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@*:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
            executable.set_parameter("when", proc.make_string_value(when.strip()))
            null = proc.parse_xml(xml_text="<null/>")
            record_body = executable.transform_to_string(xdm_node=null)
    else:
        record_body = record_body.decode()

    # TODO: validate result
    # if not valid:
    #   return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid XML")

    err = rec_update(app, prof, nr, record_body)
    logging.info(f"update app[{app}] record[{nr}] msg[{err}]")
    if (err.strip() == "404"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Record[{nr}] version was not saved as previous version couldn't be found!")
    elif (err.strip() != "OK"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
       
    return JSONResponse({"message": f"App[{app}] record[{nr}] modified"})


@router.delete("/app/{app}/record/{nr}")
@router.delete("/app/{app}/profile/{prof}/record/{nr}")
async def delete_record(request: Request, app: str, nr: str, prof: str | None=None, user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'write','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    if (prof == None):
        config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
        with open(config_file, 'r') as f:
            config = toml.load(f)
            prof = config['app']['def_prof'] 
    """
    Endpoint to delete a record based on its ID.
    If the record does not exist, it returns a 404 error.
    """
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] delete")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.info(f"{record_file} not found!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.exists(f"{record_file}.deleted"):
        os.remove(f"{record_file}.deleted")
    os.rename(record_file,f"{record_file}.deleted")

    return JSONResponse({"message": f"app[{app}] prof[{prof}] record[{nr}] deleted"})

@router.get('/app/{app}/record/editor')
@router.get('/app/{app}/profile/{prof}/record/editor')
@router.get('/app/{app}/record/{nr}/editor')
@router.get('/app/{app}/profile/{prof}/record/{nr}/editor')
def get_editor(request: Request, app: str, prof: str | None=None, nr: str | None=None, user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'write','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    if (prof == None):
        config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
        with open(config_file, 'r') as f:
            config = toml.load(f)
            prof = config['app']['def_prof'] 
    if nr:
        logging.info(f"app[{app}] prof[{prof}] record[{nr}] editor")
        record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
        if not os.path.exists(record_file):
            logging.debug(f"{record_file} doesn't exist")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        logging.info(f"app[{app}] prof[{prof}] new record editor")        
    
    if "text/html" in request.headers.get("accept", ""):
        editor = rec_editor(app,prof,nr)
        return HTMLResponse(content=editor)
    
class RecForm(str, Enum):
    json = "json"
    xml = "xml"
    html = "html"
    pdf = "pdf"

@router.get('/app/{app}/record/{nr}')
@router.get('/app/{app}/profile/{prof}/record/{nr}')
def get_record(request: Request, app: str,  nr: str, prof: str | None=None, user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'read','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})
    if (prof == None):
        config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
        with open(config_file, 'r') as f:
            config = toml.load(f)
            prof = config['app']['def_prof'] 
    if nr.count('.') == 0:
        form = "html"
    elif nr.count('.') == 1:
        nr, form = nr.rsplit('.', 1)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

    if form not in ["json", "xml", "html", "pdf"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")
    """
    Endpoint to get a record based on its ID and the application name.
    This endpoint accepts the application name and the ID as path parameters.
    If the record does not exist, it returns a 404 error.
    If the record exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] form[{form}] accept[{request.headers.get("accept", "")}]")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"

    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if form == "json" or "application/json" in request.headers.get("accept", ""):
        with PySaxonProcessor(license=False) as proc:
            rec = proc.parse_xml(xml_file_name=record_file)
            prof_doc = prof_json(app, prof)
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/rec2json.xsl")
            executable.set_parameter("prof-doc", proc.make_string_value(prof_doc))
            executable.set_parameter("rec-nr", proc.make_string_value(nr))
            result = executable.transform_to_string(xdm_node=rec)
            return JSONResponse(content=jsonable_encoder(json.loads(result)))
    elif form == RecForm.pdf or "application/pdf" in request.headers.get("accept", ""):
            html = rec_html(app,prof,nr)
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
            html = rec_html(app,prof,nr)
            return HTMLResponse(content=html)
    elif form == RecForm.xml or "application/xml" in request.headers.get("accept", ""):
        with open(record_file, 'r') as file:
            rec = file.read()
            return Response(content=rec, media_type="application/xml")

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")


@router.get("/app/{app}")
async def get_app(request: Request, app: str, user: Optional[str] = Depends(get_user_with_app)):
    if (not allowed(user,app,'read','any')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": f"Basic realm=\"{app}\""})

    """
    Endpoint to read an application based on its name.
    This endpoint accepts the application name as a path parameter.
    If the application does not exist, it returns a 404 error.
    If the application exists but the reading functionality is not implemented yet, it returns a 501 error.
    """
    logging.info(f"app[{app}]")
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        logging.debug(f"{settings.URL_DATA_APPS}/{app} doesn't exist!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    logging.debug(f"app[{app}] accept[{request.headers["Accept"]}]")
    if "text/html" in request.headers.get("accept", ""):
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/listrecs.xsl")
            executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
            executable.set_parameter("base", proc.make_string_value(settings.url_base))
            convert_toml_to_xml(f"{settings.URL_DATA_APPS}/{app}/config.toml",f"{settings.URL_DATA_APPS}/{app}/config.xml")
            config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
            executable.set_parameter("config", config)
            executable.set_parameter("app", proc.make_string_value(app))
            null = proc.parse_xml(xml_text="<null/>")
            result = executable.transform_to_string(xdm_node=null)
            return HTMLResponse(content=result)
            
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)