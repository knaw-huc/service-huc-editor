import logging
import os.path
import shutil
import toml

from fastapi import APIRouter, HTTPException, Request, Response

from saxonche import PySaxonProcessor

from starlette import status
from starlette.responses import JSONResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from src.commons import settings, convert_toml_to_xml
from src.profiles import prof_save

router = APIRouter()

@router.put("/app/{app}/profile/{id}", status_code=status.HTTP_201_CREATED)
async def create_profile(app: str, id: str):
    """
    Endpoint to create a profile based on its ID.
    If the profile already exists, it returns a message indicating that the profile already exists.
    """
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logging.info(f"app[{app}] profile[{id}] create/update")
    return await prof_save(app,id)

@router.delete("/app/{app}/profile/{id}")
async def delete_profile(request: Request, app: str, id: str):
    """
    Endpoint to mark a profile as deleted based on its ID.
    """
    logging.info(f"app[{app}] profile[{id}] delete")
    
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}/profiles//{id}"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.isdir(f"{settings.URL_DATA_APPS}/{app}/profiles/{id}.deleted"):
        shutil.rmtree(f"{settings.URL_DATA_APPS}/{app}/profiles/{id}.deleted")

    shutil.move(f"{settings.URL_DATA_APPS}/{app}/profiles/{id}", f"{settings.URL_DATA_APPS}/{app}/profiles/{id}.deleted")

    return {"message": f"Profile[{id}] is marked as deleted"}

@router.post("/app/{app}/profile/{id}/tweak", status_code=status.HTTP_201_CREATED)
async def create_profile_tweak(request: Request, app: str, id: str):
    """
    Endpoint to create a profile tweak.
    If the profile does not exist, it returns a 404 error.
    """
    logging.info(f"app[{app}] profile[{id}] modify")
    tweak_dir = f"{settings.URL_DATA_APPS}/{app}/profiles/{id}/tweaks"
    if not os.path.isdir(f"{settings.URL_DATA_APPS}/{app}/profiles/{id}"):
        logging.debug(f"profile[{id}] doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not os.path.exists(tweak_dir):
        logging.debug(f"{tweak_dir} doesn't exist")
        os.makedirs(tweak_dir)
    nr = 1
    tweak_file = f"{tweak_dir}/tweak-{nr}.xml"
    while os.path.exists(tweak_file):
        nr = nr + 1
        tweak_file = f"{tweak_dir}/tweak-{nr}.xml"
    if request.headers['Content-Type'] != 'application/xml':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml")

    tweak_body = await request.body()
    with open(tweak_file, 'wb') as file:
        file.write(tweak_body)
    return RedirectResponse(url=f"./{nr}") 

@router.put("/app/{app}/profile/{id}/tweak/{nr}")
async def modify_profile_tweak(request: Request, app:str, id: str, nr: str):
    """
    Endpoint to modify a profile tweak based on its ID and tweak NR.
    If the profile or tweak does not exist, it returns a 404 error.
    """
    logging.info(f"app[{app}] profile[{id}] tweak[{nr}] modify")
    tweak_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{id}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.debug(f"{tweak_file} doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if request.headers['Content-Type'] != 'application/xml':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/xml")

    tweak_body = await request.body()
    with open(tweak_file, 'wb') as file:
        file.write(tweak_body)

    return JSONResponse({"message": f"Profile[{id}] tweak[{nr}] modified"})

@router.delete("/app/{app}/profile/{id}/tweak/{nr}")
async def delete_profile_tweak(request: Request, app: str, id: str, nr: str):
    """
    Endpoint to delete a profile tweak based on its ID and tweak NR.
    If the profile tweak does not exist, it returns a 404 error.
    """
    logging.info(f"app[{app}] profile[{id}] tweak[{nr}] delete")
    tweak_file = f"{settings.URL_DATA_APPS}/{app}/profiles//{id}/tweaks/tweak-{nr}.xml"
    if not os.path.exists(tweak_file):
        logging.info(f"{tweak_file} not found!")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if os.path.exists(f"{tweak_file}.deleted"):
        os.remove(f"{tweak_file}.deleted")
    os.rename(tweak_file,f"{tweak_file}.deleted")

    return JSONResponse({"message": f"Profile[{id}] tweak[{nr}] deleted"})

@router.put("/app/{app}", status_code=status.HTTP_201_CREATED)
async def create_app(request: Request, app: str, descr: str | None = None, prof: str | None = None):
    """
    Endpoint to create an application based on its name.
    If the application already exists, it returns a message indicating that the application already exists.
    """
    logging.info(f"app[{app}] create")
    app_dir = f"{settings.URL_DATA_APPS}/{app}"
    if not os.path.isdir(app_dir):
        logging.debug(f"{app_dir} doesn't exist!")
        os.makedirs(f"{app_dir}")
        with open(f"{app_dir}/__init__.py", 'w') as file:
            file.write("")
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/configTemplate.xsl")
            executable.set_parameter("app", proc.make_string_value(app))
            if (descr != None):
                executable.set_parameter("descr", proc.make_string_value(descr))
            if (prof != None):
                executable.set_parameter("prof", proc.make_string_value(prof))
            executable.set_parameter("template_prof", proc.make_string_value(settings.template_prof))
            null = proc.parse_xml(xml_text="<null/>")
            config_content = executable.transform_to_string(xdm_node=null)
            config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
            with open(config_file, 'w') as file:
                file.write(config_content)
            with open(config_file, 'r') as f:
                config = toml.load(f)
                await prof_save(app,config['app']['def_prof'])
            if config['app']['def_prof'] == 'clarin.eu:cr1:p_1721373444008':
                shutil.copyfile(f"{settings.templates_dir}/HelloWorldTweak.xml",f"{settings.URL_DATA_APPS}/{app}/profiles/{config['app']['def_prof']}/tweaks/tweak-1.xml")
                shutil.copyfile(f"{settings.templates_dir}/htp.test",f"{settings.URL_DATA_APPS}/{app}/htp.test")

        static_app_dir = f"{app_dir}/resources/static"
        os.makedirs(static_app_dir)
        try:
            apps = request.app
            apps.mount( f"/app/{app}/static", StaticFiles(directory=static_app_dir), name="static")
        except Exception as e:
            logging.error(f"Error mounting static files {static_app_dir}, error message: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse({"message": f"app[{app}] is created."}, status_code=status.HTTP_201_CREATED)
    return JSONResponse({"message": f"app[{app}] already exist!"}, status_code=status.HTTP_200_OK)

@router.get('/app/{app}/config{form}')
def get_config(request: Request, app: str, form: str | None = ".toml"):
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(f"{config_file}"):
        logging.debug(f"app[{app}] doesn't exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if form not in [".toml", ".xml"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")
    if form == ".toml" or "application/toml" in request.headers.get("accept", ""):
        with open(config_file, 'r') as file:
            config = file.read()
            return Response(content=config, media_type="application/toml")
    if form == ".xml" or "application/xml" in request.headers.get("accept", ""):
        convert_toml_to_xml(config_file,f"{settings.URL_DATA_APPS}/{app}/config.xml")
        with open(f"{settings.URL_DATA_APPS}/{app}/config.xml", 'r') as file:
            config = file.read()
            return Response(content=config, media_type="application/xml")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")

@router.put('/app/{app}/config')
async def modify_config(request: Request, app: str):
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(f"{config_file}"):
        logging.debug(f"app[{app}] doesn't exist")
    if not('application/toml' in request.headers['Content-Type']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type must be application/toml!")
    config_content = await request.body()
    config_content = config_content.decode()
    #logging.info(f"app[{app}] config[{config_content}]")
    config = toml.loads(str(config_content))
    if 'application/toml' in request.headers['Content-Type']:
        with open(config_file, 'w') as file:
            file.write(toml.dumps(config))
            return JSONResponse({"message": f"App[{app}] config updated"})
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not supported")