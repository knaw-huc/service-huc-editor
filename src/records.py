import logging
import os
from saxonche import PySaxonProcessor
from src.commons import settings, convert_toml_to_xml
from src.profiles import prof_xml

def rec_html(app,prof,nr):
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
            prof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/toHTML.xsl")
            executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
            executable.set_parameter("base", proc.make_string_value(settings.url_base))
            executable.set_parameter("app", proc.make_string_value(app))
            executable.set_parameter("prof", proc.make_string_value(prof))
            executable.set_parameter("nr", proc.make_string_value(nr))
            prof = prof_xml(app, prof)
            prof = proc.parse_xml(xml_text=prof)
            executable.set_parameter("tweak-doc",prof) 
            convert_toml_to_xml(f"{settings.URL_DATA_APPS}/{app}/config.toml",f"{settings.URL_DATA_APPS}/{app}/config.xml")
            config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
            executable.set_parameter("config", config)
            return executable.transform_to_string(xdm_node=rec)

def rec_editor(app,prof,nr):
    if nr:
        logging.info(f"app[{app}] prof[{prof}] record[{nr}] editor")
    else:
        logging.info(f"app[{app}] prof[{prof}] new record editor")
    with PySaxonProcessor(license=False) as proc:
        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/editor.xsl")
        executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
        executable.set_parameter("base", proc.make_string_value(settings.url_base))
        executable.set_parameter("app", proc.make_string_value(app))
        executable.set_parameter("prof", proc.make_string_value(prof))
        if nr:
            executable.set_parameter("nr", proc.make_string_value(nr))
        convert_toml_to_xml(f"{settings.URL_DATA_APPS}/{app}/config.toml",f"{settings.URL_DATA_APPS}/{app}/config.xml")
        config = proc.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{app}/config.xml")
        executable.set_parameter("config", config)
        null = proc.parse_xml(xml_text="<null/>")
        return executable.transform_to_string(xdm_node=null)
    
def rec_update(app: str, prof: str, nr: str, rec: str) -> str:
    logging.info(f"app[{app}] prof[{prof}] record[{nr}] update")

    # does the record exist
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"
    if not os.path.isfile(record_file):
        logging.info(f"Updating app[{app}] prof[{prof}] record[{nr}] doesn't exist!")
        return "404"
    
    with PySaxonProcessor(license=False) as proc:
        old = proc.parse_xml(xml_file_name=record_file)
        new = proc.parse_xml(xml_text=rec)

        xpproc = proc.new_xpath_processor()
        xpproc.set_cwd(os.getcwd())
        xpproc.declare_namespace('clariah','http://www.clariah.eu/')
        xpproc.declare_namespace('cmd','http://www.clarin.eu/cmd/')

        xpproc.set_context(xdm_item=old)
        oprof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
        owhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        owho = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdCreator)").get_string_value()

        xpproc.set_context(xdm_item=new)
        nprof = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdProfile)").get_string_value()
        nwhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        nwho = xpproc.evaluate_single("string(/cmd:CMD/cmd:Header/cmd:MdCreator)").get_string_value()

        logging.info(f"Updating app[{app}] record[{nr}]: profile check: old[{oprof}] new[{nprof}]!")
        if oprof!=nprof:
            logging.info(f"Updating app[{app}] record[{nr}]: profile clash: old[{oprof}] new[{nprof}]!")
            return f"current profile[{oprof}] can't be changed into profile[{nprof}]!"

        logging.info(f"Updating app[{app}] record[{nr}]: when check: old[{owhen}] new[{nwhen}]!")
        if (owhen!=nwhen):
            logging.info(f"Updating app[{app}] record[{nr}]: when clash: old[{owhen}] new[{nwhen}]!")
            return f"record[{nr}] has been updated on [{owhen if '-' in owhen else datetime.fromtimestamp(int(owhen), timezone.utc)}] by [{owho}] since the record from [{nwhen if '-' in nwhen else datetime.fromtimestamp(int(nwhen), timezone.utc)}] has been read for this update by [{nwho}]!"

        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/updrec.xsl")
        executable.set_parameter("user", proc.make_string_value("service"))

        # keep the history
        cur = proc.parse_xml(xml_file_name=record_file)
        xpproc.set_context(xdm_item=cur)
        cwhen = xpproc.evaluate_single("string((/cmd:CMD/cmd:Header/cmd:MdCreationDate/@clariah:epoch,/cmd:CMD/cmd:Header/cmd:MdCreationDate,'unknown')[1])").get_string_value()
        history = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.{cwhen}.xml"
        os.rename(record_file, history)
        logging.info(f"history kept[{history}")

        rec = executable.transform_to_string(xdm_node=new)
        with open(record_file, 'w') as file:
            file.write(rec)
        logging.info(f"new version[{record_file}]")

        return "OK"