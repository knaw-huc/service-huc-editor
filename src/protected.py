import logging
import os.path
import shutil
import time
import uuid
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response
from saxonche import PySaxonProcessor
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

    shutil.move(f"{settings.URL_DATA_PROFILES}/{id}", f"{settings.URL_DATA_PROFILES}/{id}.deleted")

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
        logging.debug(f"{tweak_file} doesn't exist")
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
        logging.debug(f"{settings.URL_DATA_APPS}/{app} doesn't exist!")
        os.makedirs(f"{settings.URL_DATA_APPS}/{app}")
        return JSONResponse({"message": f"App[{app}] is created."}, status_code=status.HTTP_201_CREATED)

    return JSONResponse({"message": f"App[{app}] already exist!"}, status_code=status.HTTP_200_OK)


@router.post("/app/{app}/record/", status_code=status.HTTP_201_CREATED)
async def create_record(request: Request, app: str, prof: str | None = None, redir: str | None = "yes"):
    """
    Endpoint to create a record for an application.
    If the app does not exist, it returns a 400 error.
    """
    logging.info(f"Modifying app[{app}]: creating record")
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
    logging.info(f"Modifying app[{app}]: creating record[{nr}]")

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
        if prof == None and js["prof"] != None:
            prof = js["prof"]
        if (prof == None or prof.strip() == ""):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="When using application/json the prof query parameter should be filled!")
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/json2rec.xsl")
            executable.set_parameter("js-doc", proc.make_string_value(json.dumps(rec)))
            executable.set_parameter("user", proc.make_string_value("service"))
            executable.set_parameter("self", proc.make_string_value(f"unl://{nr}"))
            executable.set_parameter("prof", proc.make_string_value(prof.strip()))
            null = proc.parse_xml(xml_text="<null/>")
            record_body = executable.transform_to_string(xdm_node=null)
        with open(record_file, 'w') as file:
            file.write(record_body)
    else:
        with open(record_file, 'wb') as file:
            file.write(record_body)
        err = update_record(app, nr, record_body.decode())
        logging.info(f"update app[{app}] record[{nr}] msg[{err}]")
        if (err.strip() == "404"):
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Initial record[{nr}] version was not saved!")
        elif (err.strip() != "OK"):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        if redir.strip() != "no":
            return RedirectResponse(url=f"./{nr}")
    return JSONResponse({"message": f"App[{app}] record[{nr}] created","nr": nr})

def update_record(app: str, nr: str, rec: str) -> str:
    logging.info(f"Updating app[{app}] record[{nr}]")

    # does the record exist
    record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"
    if not os.path.isfile(record_file):
        logging.info(f"Updating app[{app}] record[{nr}] doesn't exist!")
        return "404"
    
    with PySaxonProcessor(license=False) as proc:
        old = proc.parse_xml(xml_file_name=record_file)
        new = proc.parse_xml(xml_text=rec)

        xpproc = proc.new_xpath_processor()
        xpproc.set_cwd(os.getcwd())
        xpproc.declare_namespace('clariah','http://www.clariah.eu/')
        xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')

        xpproc.set_context(xdm_item=old)
        oprof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
        owhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        owho = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdCreator)").get_string_value()

        xpproc.set_context(xdm_item=new)
        nprof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
        nwhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        nwho = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdCreator)").get_string_value()

        logging.info(f"Updating app[{app}] record[{nr}]: profile check: old[{oprof}] new[{nprof}]!")
        if oprof!=nprof:
            logging.info(f"Updating app[{app}] record[{nr}]: profile clash: old[{oprof}] new[{nprof}]!")
            return f"current profile[{oprof}] can't be changed into profile[{nprof}]!"

        logging.info(f"Updating app[{app}] record[{nr}]: when check: old[{owhen}] new[{nwhen}]!")
        if (owhen!=nwhen):
            logging.info(f"Updating app[{app}] record[{nr}]: when clash: old[{owhen}] new[{nwhen}]!")
            return f"record[{nr}] has been updated on [{owhen if '-' in owhen else datetime.fromtimestamp(int(owhen), timezone.utc)}] by [{owho}] since the record from [{nwhen if '-' in nwhen else datetime.fromtimestamp(int(nwhen), timezone.utc)}] has been read for this update by [{nwho}]!"

        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/updrec.xsl")
        executable.set_parameter("user", proc.make_string_value("service"))

        # keep the history
        cur = proc.parse_xml(xml_file_name=record_file)
        xpproc.set_context(xdm_item=cur)
        cwhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        history = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.{cwhen}.xml"
        os.rename(record_file, history)
        logging.info(f"history kept[{history}")

        rec = executable.transform_to_string(xdm_node=new)
        with open(record_file, 'w') as file:
            file.write(rec)
        logging.info(f"new version[{record_file}]")

        return "OK"


@router.put("/app/{app}/record/{nr}")
async def modify_record(request: Request, app: str, nr: str, prof: str | None = None, when: str | None = None):
    """
    Endpoint to create a record for an application based on its name and the record's ID.
    If the record already exists, it returns a message indicating that the record already exists.
    """
    logging.info(f"Modifying app[{app}] record[{nr}]")
    record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not('application/xml' in request.headers['Content-Type'] or 'application/json' in request.headers['Content-Type']):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml or application/json!")
    
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
            executable.set_parameter("user", proc.make_string_value("service"))
            executable.set_parameter("self", proc.make_string_value(f"unl://{nr}"))
            if (prof!=None):
                executable.set_parameter("prof", proc.make_string_value(prof.strip()))
            elif (js['prof']!=None):
                executable.set_parameter("prof", proc.make_string_value(js['prof'].strip()))
            if (when!=None):
                executable.set_parameter("when", proc.make_string_value(when.strip()))
            elif (js['when']!=None):
                executable.set_parameter("when", proc.make_string_value(js['when'].strip()))
            else:
                old = proc.parse_xml(xml_file_name=record_file)
                xpproc = proc.new_xpath_processor()
                xpproc.set_cwd(os.getcwd())
                xpproc.declare_namespace('clariah','http://www.clariah.eu/')
                xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')
                xpproc.set_context(xdm_item=old)
                when = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
            null = proc.parse_xml(xml_text="<null/>")
            record_body = executable.transform_to_string(xdm_node=null)
    else:
        record_body = record_body.decode()

    # TODO: validate result
    # if not valid:
    #   return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid XML")

    err = update_record(app, nr, record_body)
    logging.info(f"update app[{app}] record[{nr}] msg[{err}]")
    if (err.strip() == "404"):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Record[{nr}] version was not saved as previous version couldn't be found!")
    elif (err.strip() != "OK"):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
       
    return JSONResponse({"message": f"App[{app}] record[{nr}] modified"})


@router.delete("/app/{app}/record/{nr}")
async def delete_record(request: Request, app: str, nr: str):
    """
    Endpoint to delete a record based on its ID.
    If the record does not exist, it returns a 404 error.
    """
    logging.info(f"Deleting app[{app}] record[{nr}]")
    record_file = f"{settings.URL_DATA_APPS}/{app}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.info(f"{record_file} not found!")
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.exists(f"{record_file}.deleted"):
        os.remove(f"{record_file}.deleted")
    os.rename(record_file,f"{record_file}.deleted")

    return JSONResponse({"message": f"app[{app}] record[{nr}] deleted"})

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
