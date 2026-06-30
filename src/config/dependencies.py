import logging
import os
from typing import Dict, Annotated, List

import toml
from fastapi import HTTPException, Depends

from src.commons import settings



def get_all_apps():
    """
    Get all apps
    """
    return next(os.walk(settings.URL_DATA_APPS))[1]


def get_app_configuration(app: str) -> Dict:
    """
    Get the app configuration
    """
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(config_app_file):
        logging.error(f"Config file {config_app_file} does not exist")
        raise HTTPException(status_code=500, detail="Config file for this app does not exist")
    with open(config_app_file, "r") as f:
        config = toml.load(f)
        return config

ConfigDep = Annotated[Dict, Depends(get_app_configuration)]

AllAppsDep = Annotated[List[str], Depends(get_all_apps)]