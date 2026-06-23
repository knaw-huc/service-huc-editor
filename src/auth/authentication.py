import logging
import os
from typing import Optional

import toml
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic
from passlib.apache import HtpasswdFile
from saxonche import PySaxonProcessor
from starlette import status

from commons import settings, api_keys

bearer_security = HTTPBearer(auto_error=False)
security = HTTPBasic(auto_error=False)

def get_current_user(app: str, credentials: Optional[HTTPBasicCredentials] = Depends(security)):
    """
    Get the current user
    :param app: The app
    :param credentials: The credentials
    """
    if not credentials:
        # is er dan een token?
        # zo ja:
        #  heef de app config een def_user geef die dan terug anders de globale def_user
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


def get_user_with_app(app: str, basic_credentials: Optional[HTTPBasicCredentials] = Depends(security), bearer_credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_security)):
    if basic_credentials:
        return get_current_user(app, basic_credentials)
    elif bearer_credentials:
        # Handle bearer token authentication
        token = bearer_credentials.credentials
        # Implement your token validation logic
        return decode_token(token, app)

    else:
        return None


def decode_token(token: str, app: str):
    if token not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )
    return def_user(app)


def allowed(user: Optional[str], app: str, action: str, default: str, prof=None, nr=None):
    """
    :param user: The user
    :param app: The app
    :param action: The action
    :param default: The default mode
    :param prof: The profile
    :param nr: The record number/id
    """
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    if not os.path.isfile(config_app_file):
        logging.error(f"config file {config_app_file} doesn't exist")
        if default == "any":
            return True
        return False
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        mode = default
        if 'access' in config["app"]:
            if action in config['app']['access']:
                mode = config['app']['access'][action]
        if mode == "owner" and user is not None and prof is not None and nr is not None:
            record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
            with open(record_file, 'r') as file:
                rec = file.read()
                with PySaxonProcessor(license=False) as proc:
                    rec = proc.parse_xml(xml_text=rec)
                    xpproc = proc.new_xpath_processor()
                    xpproc.set_cwd(os.getcwd())
                    xpproc.declare_namespace('clariah','http://www.clariah.eu/')
                    xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')
                    xpproc.set_context(xdm_item=rec)
                    owner = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()
                    if owner == user:
                        return True
        elif mode == "owner" and user is not None:
                return True
        elif mode == "users" and user is not None:
            return True
        elif mode == "any":
            return True
    return False


def def_user(app: str):
    """
    Get the default user for the application.
    :param app: The app for which the default user should be returned
    """
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        if 'def_user' in config["app"]:
            return config["app"]['def_user']
        elif 'def_user' in settings:
            return settings.def_user
        return "server"
