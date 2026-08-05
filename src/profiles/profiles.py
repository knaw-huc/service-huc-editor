import logging
import os
import pathlib
import requests as req

from fastapi import HTTPException
from starlette import status
from saxonche import PySaxonProcessor
from src.commons import settings, tweak_nr

async def get_profile_from_clarin(profile_id):
    """
    Get the profile from ccr
    :param profile_id:
    :return:
    """
    clarin_url = settings.URL_CLARIN_COMPONENT_REGISTRY % profile_id
    logging.debug(f"{clarin_url}")
    clarin_profile = req.get(clarin_url)
    if clarin_profile.status_code != status.HTTP_200_OK:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return clarin_profile.content

async def prof_save(app: str, id: str):
    """
    Save the profile
    :param app:
    :param id:
    :return:
    """
    profile_path = f"{settings.URL_DATA_APPS}/{app}/profiles/{id}"
    profile_xml = await get_profile_from_clarin(id)
    if not os.path.isdir(profile_path):
        os.makedirs(f"{profile_path}/tweaks")
        os.makedirs(f"{profile_path}/records")
        with open(os.path.join(profile_path, f'{id}.xml'), 'wb') as file:
            file.write(profile_xml)
        return {"message": f"Profile[{id}] is created"}
    else:
        with open(os.path.join(profile_path, f'{id}.xml'), 'wb') as file:
            file.write(profile_xml)
            return {"message": f"Profile[{id}] is refreshed"}

def prof_xml(app: str, id: str):
    """
    Get the profile as XML
    :param app:
    :param id:
    :return:
    """
    logging.info(f"app[{app}] prof[{id}] get XML")
    profile_path = f"{settings.URL_DATA_APPS}/{app}/profiles/{id}"
    with open(os.path.join(profile_path, f'{id}.xml'), 'r') as file:
        # Reading data from the xml file
        prof = file.read()
        tweaks = [t for t in pathlib.Path(f"{profile_path}/tweaks/").glob("tweak-*.xml")]
        tweaks.sort(key=tweak_nr)
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/mergeTweak.xsl")
            for tf in tweaks:
                with open(tf, 'r') as file:
                    logging.info(f"profile[{id}] apply tweak[{tf}]")
                    executable.set_parameter("tweakFile", proc.make_string_value(str(tf)))
                    pnode = proc.parse_xml(xml_text=prof)
                    prof = executable.transform_to_string(xdm_node=pnode)
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/lastTweak.xsl")
            logging.info(f"profile[{id}] applied lastTweak")
            pnode = proc.parse_xml(xml_text=prof)
            prof = executable.transform_to_string(xdm_node=pnode)
        return prof

def prof_json(app: str, profile_id: str):
    """
    Get the profile as JSON
    :param app:
    :param profile_id:
    :return:
    """
    prof = prof_xml(app, profile_id)
    if prof:
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(
                stylesheet_file=f"{settings.xslt_dir}/prof2json.xsl")
            node = proc.parse_xml(xml_text=prof)
            return  executable.transform_to_string(xdm_node=node)
    return None

def prof_json2(app: str, id:str):
    prof = prof_xml(app, id)
    if (prof):
            with PySaxonProcessor(license=False) as proc:
                xsltproc = proc.new_xslt30_processor()
                xsltproc.set_cwd(os.getcwd())
                executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/prof2json-2.xsl")
                node = proc.parse_xml(xml_text=prof)
                return  executable.transform_to_string(xdm_node=node)
    return None