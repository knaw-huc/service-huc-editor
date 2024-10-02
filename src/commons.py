import importlib.metadata
import logging
import re

from dynaconf import Dynaconf
import requests as req
from fastapi import HTTPException
from starlette import status

import toml
import xml.etree.ElementTree as ET

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

def tweak_nr(tf):
    nr = re.sub('.*/tweak-([0-9]+).xml','\\1',str(tf))
    logging.info(f"tweak[{tf}] nr[{nr}]")
    return int(nr)


def dict_to_xml(tag, d):
    """
    Convert a dictionary to an XML element.

    Args:
        tag (str): The root tag for the XML element.
        d (dict): The dictionary to convert to XML.

    Returns:
        xml.etree.ElementTree.Element: The XML element representing the dictionary.

    This function recursively converts a dictionary to an XML element. Each key-value pair
    in the dictionary is converted to a child element of the root tag. If a value is a nested
    dictionary, the function calls itself recursively to convert the nested dictionary.
    """
    elem = ET.Element(tag)
    for key, val in d.items():
        child = ET.Element(key)
        child.text = str(val) if not isinstance(val, dict) else None
        elem.append(child if not isinstance(val, dict) else dict_to_xml(key, val))
    return elem


def convert_toml_to_xml(toml_file: str, xml_file: str):
    """
    Convert a TOML file to an XML file.

    Args:
        toml_file (str): The path to the input TOML file.
        xml_file (str): The path to the output XML file.

    This function reads the contents of a TOML file, converts it to an XML format,
    and writes the resulting XML to a specified file.

    Example:
        convert_toml_to_xml('config.toml', 'config.xml')
    """
    # Read the TOML file
    toml_data = toml.load(toml_file)

    # Create XML root and build the tree
    root = dict_to_xml('root', toml_data)
    tree = ET.ElementTree(root)

    # Write the XML to a file
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)