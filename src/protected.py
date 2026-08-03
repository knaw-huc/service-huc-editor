import logging
import os.path
import time
import json
import toml

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder

from saxonche import PySaxonProcessor

from starlette import status
from starlette.responses import JSONResponse, RedirectResponse

from typing import Optional, Annotated

from src.config.dependencies import ConfigDep, ProfileDep
from src.auth.models import User
from src.auth.authentication import get_user_with_app, allowed, def_user
from src.commons import settings, call_record_hook, call_action_hook
from src.records.records import rec_update, rec_history,  rec_form
from src.profiles.profiles import prof_xml
from src.records.services import RecordManagerDep
from src.xslt import StylesheetProcessor, StylesheetDep, SaxonProcessorDep, RecordMetadataDep

router = APIRouter(
    prefix="/app/{app}/profile/{prof}",
)


@router.get("/records/")
async def get_records(
    app: str,
    profile: ProfileDep,
    record_manager: RecordManagerDep,
    record_metadata: RecordMetadataDep,
    config: ConfigDep,
    offset: int = 0,
    limit: int = 100,
    user: Optional[User] = Depends(get_user_with_app)):
    """
    Get records for the given application and profile.
    :param record_metadata:
    :param config:
    :param app:
    :param profile:
    :param record_manager:
    :param offset:
    :param limit:
    :param user:
    :return:
    """
    if not allowed(user, app, 'read', 'any'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!",
                            headers={"WWW-Authenticate": "Bearer"})
    records = record_manager.list(start=offset, limit=limit)
    total = record_manager.num_records()

    data = list(map(lambda x : x.table_data(user, config), records))

    return {
        "header": [
            {
                "prop": key,
                "label": value["label"],
                "sort": value["sort"] == "true",
                "filter": value["filter"] == "true" if value["filter"] != "'select'" else "select",
            } for key, value in profile["list"].items()
        ],
        "actions": {
            key: action for key, action in config["app"]["hooks"]["action"].items() if "rec" in action["level"].split(" ")
        },
        "data": data,
        "offset": offset,
        "limit": limit,
        "total": total,
    }


@router.post("/record/", status_code=status.HTTP_201_CREATED)
async def create_record(
        request: Request,
        app: str,
        record_manager: RecordManagerDep,
        proc: SaxonProcessorDep,
        json_sheet: StylesheetProcessor = Depends(StylesheetDep("json2rec")),
        post_tweak_sheet: StylesheetProcessor = Depends(StylesheetDep("postTweak")),
        prof: str | None = None,
        redir: str | None = "yes",
        user: Optional[User] = Depends(get_user_with_app)):
    """
    Endpoint to create a record for an application.
    If the app does not exist, it returns a 400 error.
    """
    record_body = await request.body()
    trace_dir = f"{settings.URL_DATA_APPS}/{app}/trace"
    if not os.path.exists(trace_dir):
        os.makedirs(trace_dir)
    epoch = time.time()
    trace_file = f"{trace_dir}/create_record-{request.client.host}.{epoch}"
    with open(trace_file, 'wb') as file:
        file.write(record_body)

    if not allowed(user, app, 'write', 'any'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})

    config = None
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
    if prof is None:
        prof = config['app']['def_prof']

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
    deleted = f"{record_dir}/history/record-{nr}.xml.deleted"
    while os.path.exists(record_file) or os.path.exists(deleted):
        nr = nr + 1
        record_file = f"{record_dir}/record-{nr}.xml"
        deleted = f"{record_dir}/history/record-{nr}.xml.deleted"
    logging.info(f"app[{app}] record[{nr}] create")

    if not('application/xml' in request.headers['Content-Type'] or 'application/json' in request.headers['Content-Type']):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type must be application/xml or application/json!")

    if 'application/json' in request.headers['Content-Type']:
        logging.info(f"record[{nr}] JSON to XML]")
        logging.info(f"- body JSON[{json.dumps(json.loads(record_body))}]")
        js = json.loads(record_body)
        rec = js
        if js["record"] is not None:
            rec = js["record"]
        logging.info(f"- record JSON[{json.dumps(rec)}]")
        if prof is not None and js["prof"] is not None and prof != js["prof"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The profile in the path (or the app default) and the profile in the JSON differ! ({prof}!={js['prof']})")
        if 'cmdi_version' in config["app"]:
            json_sheet.set_parameter("vers", config["app"]["cmdi_version"])
        if user is None:
            user = def_user(app)
        json_sheet.set_parameter("js-doc", json.dumps(rec))
        json_sheet.set_parameter("user", user.name)
        json_sheet.set_parameter("self", f"unl://{nr}")
        json_sheet.set_parameter("prof", prof.strip() if prof is not None else "")
        rec = json_sheet.main()
        logging.info(f"- record XML[{rec}]")
        rec, msg = call_record_hook("create_pre",app,prof,nr,user.name,rec)
        if rec is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        with open(record_file, 'w') as file:
            file.write(str(rec))
        logging.info(f"created[JSON] app[{app}] prof[{prof}] record[{nr}]")

    else: # XML input
        rec = proc.parse_xml(xml_text=record_body)
        rec, msg = call_record_hook("create_pre",app,prof,nr,user.name,rec)
        if rec is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
        with open(record_file, 'w') as file:
            file.write(str(rec))
            # update to add the epoch
            res, when = rec_update(app, prof, str(nr), str(rec))
            logging.info(f"created[XML] app[{app}] prof[{prof}] record[{nr}] msg[{res}]")
            if res.strip() == "404":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Initial record[{nr}] version was not saved!")
            elif res.strip() != "OK":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)

    tweak = prof_xml(app, prof)
    tweak = proc.parse_xml(xml_text=tweak)
    post_tweak_sheet.set_parameter("prof", prof)
    post_tweak_sheet.set_parameter("nr", str(nr))
    post_tweak_sheet.set_parameter("tweak-doc", tweak)
    rec = post_tweak_sheet.apply(record=str(nr), profile=prof)

    with open(record_file, 'w') as file:
        file.write(str(rec))

    record_manager.add_record(nr)

    call_record_hook("create_post",app,prof,nr,user)
    headers = {}
    if redir.strip() != "no":
        headers = {"Location": f"./{nr}"}
    xpproc = proc.new_xpath_processor()
    xpproc.declare_namespace('clariah','http://www.clariah.eu/')
    xpproc.set_context(file_name=record_file)
    when = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
    return JSONResponse(status_code=201,headers=headers,content={"message": f"app[{app}] prof[{prof}] record[{nr}] created","nr": nr,"when":when})

@router.put("/record/{nr}")
async def modify_record(request: Request, app: str, nr: str,
                        record_manager: RecordManagerDep,
                        prof: str | None = None,
                        when: str | None = None, user: Optional[User] = Depends(get_user_with_app)):
    """
    Endpoint to create a record for an application based on its name and the record's ID.
    If the record already exists, it returns a message indicating that the record already exists.
    """
    record_body = await request.body()
    trace_dir = f"{settings.URL_DATA_APPS}/{app}/trace"
    if not os.path.exists(trace_dir):
        os.makedirs(trace_dir)
    epoch = time.time()
    trace_file = f"{trace_dir}/modify_record-{request.client.host}.{epoch}"
    with open(trace_file, 'wb') as file:
        file.write(record_body)

    config=None
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
    if prof is None:
        prof = config['app']['def_prof']
    if not allowed(user, app, 'write', 'any', prof, nr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] modify")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not('application/xml' in request.headers['Content-Type'] or 'application/json' in request.headers['Content-Type']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml or application/json!")

    if 'application/json' in request.headers['Content-Type']:
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/json2rec.xsl")
            logging.info(f"record[{nr}] JSON to XML]")
            logging.info(f"- body JSON[{record_body}]")
            js = json.loads(record_body)
            rec = js
            if js['record'] is not None:
                rec = js['record']
            logging.info(f"- record JSON[{json.dumps(rec)}]")
            executable.set_parameter("js-doc", proc.make_string_value(json.dumps(rec)))
            if user is None:
                user = def_user(app)
            executable.set_parameter("user", proc.make_string_value(user.name))
            if 'cmdi_version' in config["app"]:
                executable.set_parameter("vers", proc.make_string_value(config['app']['cmdi_version']))
            executable.set_parameter("self", proc.make_string_value(f"unl://{nr}"))
            if prof is not None and js["prof"] is not None and prof != js["prof"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The profile in the path (or the app default) and the profile in the JSON differ! ({prof}!={js['prof']})")
            executable.set_parameter("prof", proc.make_string_value(prof.strip()))
            if when is None:
                if js['when'] is not None:
                    when = js['when']
                else:
                    old = proc.parse_xml(xml_file_name=record_file)
                    xpproc = proc.new_xpath_processor()
                    xpproc.set_cwd(os.getcwd())
                    xpproc.set_context(xdm_item=old)
                    when = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@*:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
            executable.set_parameter("when", proc.make_string_value(when.strip()))
            record_body = executable.call_template_returning_string("main")
            logging.info(f"- record XML[{rec}]")
    else:
        record_body = record_body.decode()

    # TODO: validate result
    # if not valid:
    #   return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid XML")
    with PySaxonProcessor(license=False) as proc:
        rec = proc.parse_xml(xml_text=record_body)
        rec, msg = call_record_hook("update_pre",app,prof,nr,user,rec)
        if rec is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        res, when = rec_update(app, prof, nr, str(rec))
        logging.info(f"updated app[{app}] record[{nr}] msg[{res}]")
        if res.strip() == "404":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Record[{nr}] version was not saved as previous version couldn't be found!")
        elif res.strip() != "OK":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)

        call_record_hook("update_post",app,prof,nr,user)

        record_manager.update_record(nr)

        return JSONResponse({"message": f"App[{app}] record[{nr}] modified", "when": when})


@router.delete("/record/{nr}")
async def delete_record(request: Request, app: str, nr: str,
                        record_manager: RecordManagerDep,
                        prof: str | None=None, user: Optional[User] = Depends(
    get_user_with_app)):
    """
    Endpoint to delete a record based on its ID.
    If the record does not exist, it returns a 404 error.
    """
    if (prof == None):
        config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
        with open(config_file, 'r') as f:
            config = toml.load(f)
            prof = config['app']['def_prof']
    if not allowed(user, app, 'write', 'any', prof, nr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] delete")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.exists(record_file):
        logging.info(f"{record_file} not found!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    history_dir = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/history"
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    with PySaxonProcessor(license=False) as proc:
        rec = proc.parse_xml(xml_file_name=record_file)
        rec, msg = call_record_hook("delete_pre",app,prof,nr,user,rec)
        if rec is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    deleted = f"{history_dir}/record-{nr}.xml.deleted"
    if os.path.exists(deleted):
        os.remove(deleted)
    os.rename(record_file,deleted)

    call_record_hook("delete_post",app,prof,nr,user)

    record_manager.delete_record(nr)

    return JSONResponse({"message": f"app[{app}] prof[{prof}] record[{nr}] deleted"})


@router.get('/record/{nr}/history/{epoch}')
def get_version(request: Request, app: str, nr: int, epoch:str, prof: str | None=None, user: Optional[User] = Depends(
    get_user_with_app)):
    # yes it works also http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3.xml/history/1767225600 with the same extensions to the record number for a correct format

    # DONE specifieke versie van een record tonen
    # http://localhost:1210/app/stalling/profile/clarin.eu:cr1:p_1708423613607/record/3/history/1767225600 
    # 1-1-2026 00:00:00

    # MPpseudocode: get a list of epochs from history folder, (it's in their name)
    #               determine the 'closest' one 
    #               get that file
    #               server that file in a certain format?
    # 
    # 
    if prof is None:
        config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
        with open(config_file, 'r') as f:
            config = toml.load(f)
            prof = config['app']['def_prof']
    if epoch.count('.') == 0:
        ext = None
    elif epoch.count('.') == 1:
        epoch, ext = epoch.rsplit('.', 1)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

    if not allowed(user, app, 'read', 'any', prof, nr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})

    logging.info(f"app[{app}] prof[{prof}] record[{nr}] epoc[{epoch}]form[{ext}] accept[{request.headers.get("accept", "")}]")

    # juiste history file bepalen
    data_dict = rec_history(app, prof, nr)
    # data_dict = json.loads(raw_json)
    epochs = [item['epoch'] for item in data_dict['history']]
    epoch = int(epoch)  # unix timestamp, given in url
    closest_epoch = min(epochs, key=lambda x: abs(x - epoch))
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/history/record-{nr}.{closest_epoch}.xml"

    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with PySaxonProcessor(license=False) as proc:
        rec = proc.parse_xml(xml_file_name=record_file)

        (res, form, mime) = rec_form(app,prof,nr,proc,rec,ext,request.headers.get("accept"))

        if form in ['json','json2']:
            return JSONResponse(content=jsonable_encoder(res))
        else:
            return Response(res, headers={'Content-Disposition': f'inline; filename="{app}-record-{nr}.{form}"'}, media_type=mime)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

@router.get('/record/{nr}')
def get_record(request: Request, app: str, nr: str, config: ConfigDep, proc: SaxonProcessorDep,
               prof: str | None=None, user: Optional[User] = Depends(
    get_user_with_app)):
    """

    :param request:
    :param app: App name
    :param nr: Record number
    :param config: The app config from the toml file
    :param proc: Saxon processor
    :param prof: Profile name
    :param user: The user, if logged in
    :return:
    """
    if prof is None:
        prof = config['app']['def_prof']
    if nr.count('.') == 0:
        ext = None
    elif nr.count('.') == 1:
        nr, ext = nr.rsplit('.', 1)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

    if not allowed(user, app, 'read', 'any', prof, nr):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!",
                            headers={"WWW-Authenticate": "Bearer"})

    logging.info(f"app[{app}] prof[{prof}] record[{nr}] form[{ext}] accept[{request.headers.get("accept","")}]")
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"

    if not os.path.exists(record_file):
        logging.debug(f"{record_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rec = proc.parse_xml(xml_file_name=record_file)
    rec, msg = call_record_hook("read_pre",app,prof,nr,user.name,rec)
    if rec is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    (res, form, mime) = rec_form(app,prof,nr,proc,rec,ext,request.headers.get("accept"))

    call_record_hook("read_post",app,prof,nr,user.name)

    if form in ['json','json2']:
        return JSONResponse(content=jsonable_encoder(res))
    return Response(res,
                    headers={'Content-Disposition': f'inline; filename="{app}-record-{nr}.{form}"'},
                    media_type=mime)


@router.get('/entity/')
@router.get('/entity/{ent}')
async def get_refs(request: Request, app: str, config: ConfigDep, prof: str | None=None,
                   ent: str | None=None, q: str = "*",
                   stylesheet: StylesheetProcessor = Depends(StylesheetDep('listents')),
                   user: Optional[User] = Depends(get_user_with_app)):
    """
    Get refs
    :param request:
    :param app:
    :param config:
    :param prof:
    :param ent:
    :param q:
    :param stylesheet:
    :param user:
    :return:
    """
    if not allowed(user, app, 'read', 'any'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})
    if prof is None:
        prof = config['app']['def_prof']
    if ent is None:
        for key in config["app"]["prof"].keys():
            if config["app"]["prof"][key]["prof"] == prof:
                ent=key
    #TODO: check that prof and ent lead somewhere
    if q.startswith('^'):
        q = q.removeprefix('^') + "*"
    elif '*' not in q:
        q = "*" + q + "*"

    logging.info(f"app[{app}] prof[{prof}] enity[{ent}] query[{q}] user[{user}] accept[{request.headers.get("accept", "")}]")
    stylesheet.set_parameter("prof", prof)
    stylesheet.set_parameter("ent", ent)
    stylesheet.set_parameter("query", q)
    if user is not None:
        stylesheet.set_parameter("user", user.name)
    else:
        stylesheet.set_parameter("user", def_user(app).name)
    result = stylesheet.apply()
    logging.info(f"result[{result}]")
    return JSONResponse(content=jsonable_encoder(json.loads(result)))


@router.get('/entity/{id}')
@router.get('/entity/{ent}/{id}')
async def get_ref(request: Request, app: str, id:str, prof: str | None=None, ent: str | None=None, user: Optional[User] = Depends(
    get_user_with_app)):
    if not allowed(user, app, 'read', 'any'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not allowed!", headers={"WWW-Authenticate": "Bearer"})
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        if (prof == None):
            config = toml.load(f)
            prof = config['app']['def_prof']
        if (ent == None):
            for key in config["app"]["prof"].keys():
                if config["app"]["prof"][key]["prof"] == prof:
                    ent=key
        #TODO: check that prof and ent lead somewhere
        logging.info(f"app[{app}] prof[{prof}] enity[{ent}] id[{id}] user[{user}] accept[{request.headers.get("accept", "")}]")
        return RedirectResponse(url=f"/app/{app}/profile/{prof}/record/{id}")


@router.get('/action/{action}')
@router.get('/record/{nr}/action/{action}')
def get_action(req: Request, app: str, action: str, config: ConfigDep,
               prof: str | None=None, nr: str | None=None, user: Optional[User] = Depends(
            get_user_with_app)):
    """
    Get action
    :param req:
    :param app:
    :param action:
    :param config:
    :param prof:
    :param nr:
    :param user:
    :return:
    """
    if nr is not None and prof is None:
        prof = config['app']['def_prof']
    return call_action_hook(req,action,app,prof,nr,user)
