import importlib
import importlib.metadata
import logging
import os
import re
import ast
import xml.dom.minidom



from saxonche import PySaxonProcessor, PyXdmNode

from dynaconf import Dynaconf
import jinja2
from fastapi import Request

import toml
import xml.etree.ElementTree as ET

os.environ["BASE_DIR"] = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = Dynaconf(
    settings_files=['conf/*settings.toml', 'conf/.secrets.toml'],
    root_path=os.getenv("BASE_DIR"), environments=True
)

api_keys = [
    settings.SERVICE_HUC_EDITOR_API_KEY
]  # Todo: This is encrypted in the .secrets.toml


logging.basicConfig(filename=settings.log_file, level=settings.log_level,
                    format=settings.log_format)

data = {}
#__version__ = importlib.metadata.metadata(settings.service_name)["version"]
data.update({"service-version": "0.1.10"})


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

def call_record_hook(crud:str,app:str,prof:str,nr:str,user:str,rec:PyXdmNode | None = None ) -> tuple[PyXdmNode, str]:
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
        if "hooks" in config['app'] and "record" in config["app"]["hooks"] and crud in config["app"]["hooks"]["record"]:
            logging.info(f"call_record_hook(hook[{config['app']['hooks']['record'][crud]}],app[{app}],rec[{nr}])")
            if crud.endswith("_pre"):
                rec, msg = call_record_pre_hook(config['app']['hooks']['record'][crud],crud.replace('_pre',''),app,prof,nr,user,rec)
                logging.info(f"call_record_hook(hook[{config['app']['hooks']['record'][crud]}],app[{app}],rec[{nr}]) -> rec[{rec}], msg[{msg}]")
                return rec, msg
            if crud.endswith("_post"):
                call_record_post_hook(config['app']['hooks']['record'][crud],crud.replace('_post',''),app,prof,nr,user)
                return rec, None
        else:
            logging.info(f"no hook[{crud}]!")
            return rec, None

def call_record_pre_hook(hook:str,crud:str,app:str,prof:str,nr:str,user:str,rec:PyXdmNode) -> tuple[PyXdmNode, str]:
    # import hook from data/apps/app/src/hooks.py
    mod = importlib.import_module(f"apps.{app}.src.hooks")
    # call hook(app,rec)
    func = getattr(mod,hook)
    rec, msg = func(crud,app,prof,nr,user,rec)
    return rec, msg

def call_record_post_hook(hook:str,crud:str,app:str,prof:str,nr:str,user:str ) -> None:
    # import hook from data/apps/app/src/hooks.py
    mod = importlib.import_module(f"apps.{app}.src.hooks")
    # call hook(app,rec)
    func = getattr(mod,hook)
    func(crud,app,prof,nr,user)

def call_action_hook(req: Request,action:str,app:str,prof:str,rec:str,user:str):
    config_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_file, 'r') as f:
        config = toml.load(f)
        logging.info('config: %s',config)
        if "hooks" in config['app']:
            if "action" in config["app"]["hooks"]:
                if action in config["app"]["hooks"]["action"]:
                    if "hook" in config["app"]["hooks"]["action"][action]:
                        enabled = True
                        if rec!=None:
                            enable="true()"
                            if "enable" in  config["app"]["hooks"]["action"][action]:
                                enable = config["app"]["hooks"]["action"][action]["enable"]
                            with PySaxonProcessor(license=False) as proc:
                                xpproc = proc.new_xpath_processor()
                                record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{rec}.xml"
                                node = proc.parse_xml(xml_file_name=record_file)
                                xpproc.set_context(xdm_item=node)
                                self = xpproc.evaluate_single('//*:MdSelfLink')
                                xpproc.declare_variable('self')
                                xpproc.set_parameter('self',self)
                                enabled = xpproc.effective_boolean_value(enable)
                        if enabled:
                            # import hook from data/apps/app/src/hooks.py
                            mod = importlib.import_module(f"apps.{app}.src.hooks")
                            # call hook(app,rec)
                            func = getattr(mod,config["app"]["hooks"]["action"][action]["hook"])
                            logging.info(f' calling hook[{config["app"]["hooks"]["action"][action]["hook"]}]!')
                            return func(req,action,app,prof,rec,user)
                    else:
                        logging.info(f"no action hook[{action}]!")
                else:
                    logging.info(f" no action {action}!")
            else:
                logging.info(f" no action!")
        else:
            logging.info(f"no hooks!")
            return None

def allowed(user,app,action,default,prof=None,nr=None):
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
        if mode == "owner" and user!=None and prof!=None and nr!=None:
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
        elif mode == "owner" and user!=None:
                return True
        elif mode == "users" and user != None:
            return True
        elif mode == "any":
            return True
    return False
    
def def_user(app):
    config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
    with open(config_app_file, 'r') as f:
        config = toml.load(f)
        if 'def_user' in config["app"]:
            return config["app"]['def_user']
        elif 'def_user' in settings:
            return settings.def_user
        return "server"
