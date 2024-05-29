import importlib.metadata
import logging

from dynaconf import Dynaconf


settings = Dynaconf(settings_files=["conf/settings.toml", "conf/.secrets.toml"],
                    environments=True)
logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)
data = {}


__version__ = importlib.metadata.metadata(settings.SERVICE_NAME)["version"]
data.update({"service-version": __version__})
