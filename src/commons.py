import importlib.metadata
import logging

from dynaconf import Dynaconf
import requests as req
from fastapi import HTTPException
from starlette import status

settings = Dynaconf(settings_files=["conf/settings.toml", "conf/.secrets.toml"],
                    environments=True)
logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)
data = {}


__version__ = importlib.metadata.metadata(settings.SERVICE_NAME)["version"]
data.update({"service-version": __version__})


async def get_profile_from_clarin(id):
    clarin_url = settings.URL_CLARIN_COMPONENT_REGISTRY % id
    logging.debug(f"{clarin_url}")
    clarin_profile = req.get(clarin_url)
    if clarin_profile.status_code != status.HTTP_200_OK:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return clarin_profile.content
