import importlib
import importlib.metadata
import logging
import os
import re
import ast
import xml.dom.minidom

from dynaconf import Dynaconf
import requests as req

import toml
import xml.etree.ElementTree as ET

os.environ["BASE_DIR"] = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = Dynaconf(
    settings_files=['conf/*settings.toml', 'conf/.secrets.toml'],
    root_path=os.getenv("BASE_DIR"), environments=True
)

logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)
data = {}


__version__ = importlib.metadata.metadata(settings.SERVICE_NAME)["version"]
data.update({"service-version": __version__})


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

        try:
            evaluated_list = ast.literal_eval(str(val))

            # Check if the evaluated result is a list
            is_list = isinstance(evaluated_list, list)
            if is_list:
                child = ET.Element(key)
                elem.append(child)
                for item in evaluated_list:
                    item_el = ET.Element("item")
                    item_el.text = item
                    child.append(item_el)
        except:
            pass

        elem.append(child if not isinstance(val, dict) else dict_to_xml(key, val))
    return elem



def convert_toml_to_xml(toml_file: str, xml_file: str, root_element: str = "config"):
    """
    Convert a TOML file to an XML file.

    Args:
        toml_file (str): The path to the input TOML file.
        xml_file (str): The path to the output XML file.
        root_element (str): The root element name for the XML. Defaults to "config".

    This function reads the contents of a TOML file, converts it to an XML format,
    and writes the resulting XML to a specified file.

    Example:
        convert_toml_to_xml('config.toml', 'config.xml')
    """
    try:
        # Read the TOML file
        toml_data = toml.load(toml_file)
    except FileNotFoundError:
        # Log an error if the file is not found and raise a ValueError
        logging.error(f"File not found: {toml_file}")
        raise ValueError("File not found")
    except toml.TomlDecodeError as e:
        # Log an error if there is an issue decoding the TOML file and raise a ValueError
        logging.error(f"Error decoding TOML file: {e}")
        raise ValueError("Error decoding TOML file")

    # Create XML root and build the tree
    root = dict_to_xml(root_element, toml_data)
    tree = ET.ElementTree(root)

    # Convert the XML tree to a string
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    # Parse the string with minidom
    reparsed = xml.dom.minidom.parseString(rough_string)
    # Pretty-print the XML
    pretty_xml = reparsed.toprettyxml(indent="  ")

    # Write the pretty-printed XML to a file
    with open(xml_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

def call_record_create_hook(hook,app,rec):
    # import hook from data/apps/app/src/hooks.py
    mod = importlib.import_module(f"apps.{app}.src.hooks")
    # call hook(app,rec)
    func = getattr(mod,hook)
    func(app,rec)

def allowed(user,app,action,default):
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

        if mode == "users" and user != None:
            return True
        if mode == "any":
            return True
    return False
