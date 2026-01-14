import logging
import os
import datetime
import toml
from datetime import timezone 

from saxonche import PySaxonProcessor
from src.commons import settings, convert_toml_to_xml, def_user
from src.profiles import prof_xml

from time import strftime, localtime
from datetime import datetime
import math
import glob
import operator




def rec_html(app,prof,nr):
    logging.info(f"app[{app}] prof[{prof}] rec[{nr}] get HTML")
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
            if prof == None:
                prof = xpproc.evaluate_single("string(/*:CMD/*:Header/*:MdProfile)").get_string_value()
            xsltproc = proc.new_xslt30_processor()
            xsltproc.set_cwd(os.getcwd())
            sheet=f"{settings.xslt_dir}/toHTML.xsl"
            config_app_file = f"{settings.URL_DATA_APPS}/{app}/config.toml"
            if not os.path.isfile(config_app_file):
                logging.error(f"config file {config_app_file} doesn't exist")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App config file not found")
            logging.info(f"config[{config_app_file}]")
            with open(config_app_file, 'r') as f:
                config = toml.load(f)
                if 'prof' in config["app"]:
                    for profile in config['app']['prof'].keys():
                        logging.info(f"profile[{profile}]")
                        if config["app"]["prof"][profile]["prof"]==prof:
                            logging.info(f"profile[{profile}={prof}]")
                            if "html" in config["app"]["prof"][profile].keys():
                                overload = f"{settings.URL_DATA_APPS}/{app}/resources/xslt/{config['app']["prof"][profile]["html"]}"
                                logging.info(f"HTML overload[{overload}]")
                                if os.path.isfile(overload):
                                    sheet = overload
            logging.info(f"HTML[{sheet}]")
            executable = xsltproc.compile_stylesheet(stylesheet_file=sheet)
            executable.set_parameter("cwd", proc.make_string_value(os.getcwd()))
            executable.set_parameter("base", proc.make_string_value(settings.url_base))
            executable.set_parameter("app", proc.make_string_value(app))
            executable.set_parameter("prof", proc.make_string_value(prof))
            executable.set_parameter("nr", proc.make_string_value(nr))
            prof = prof_xml(app, prof)
            prof = proc.parse_xml(xml_text=prof)
            executable.set_parameter("tweak-doc",prof) 
            convert_toml_to_xml(toml_file=config_app_file,xml_file=f"{settings.URL_DATA_APPS}/{app}/config.xml")
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
        executable.set_parameter("cdn", proc.make_string_value(settings.url_cdn))
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
        oprof = xpproc.evaluate_single("string(/*:CMD/*:Header/*:MdProfile)").get_string_value()
        owhen = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
        owho = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()

        xpproc.set_context(xdm_item=new)
        nprof = xpproc.evaluate_single("string(/*:CMD/*:Header/*:MdProfile)").get_string_value()
        nwhen = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
        nwho = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()

        logging.info(f"Updating app[{app}] record[{nr}]: profile check: old[{oprof}] new[{nprof}]!")
        if oprof!=nprof:
            logging.info(f"Updating app[{app}] record[{nr}]: profile clash: old[{oprof}] new[{nprof}]!")
            return f"current profile[{oprof}] can't be changed into profile[{nprof}]!"

        logging.info(f"Updating app[{app}] record[{nr}]: when check: old[{owhen}] new[{nwhen}]!")
        if (owhen!=nwhen):
            logging.info(f"Updating app[{app}] record[{nr}]: when clash: old[{owhen}] new[{nwhen}]!")
            return f"record[{nr}] has been updated on [{owhen if ('-' in owhen) or (owhen=="unknown") else datetime.datetime.fromtimestamp(int(owhen), timezone.utc)}] by [{owho}] since the record (version from [{nwhen if '-' in nwhen else datetime.datetime.fromtimestamp(int(nwhen), timezone.utc)}]) has been read at for this update by [{nwho}]!", "unknown"

        xsltproc = proc.new_xslt30_processor()
        xsltproc.set_cwd(os.getcwd())
        executable = xsltproc.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/updrec.xsl")
        executable.set_parameter("user", proc.make_string_value(nwho))

        # keep the history
        history_dir = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/history"
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        cur = proc.parse_xml(xml_file_name=record_file)
        xpproc.set_context(xdm_item=cur)
        cwhen = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
        history = f"{history_dir}/record-{nr}.{cwhen}.xml"
        os.rename(record_file, history)
        logging.info(f"history kept[{history}")

        rec = executable.transform_to_string(xdm_node=new)
        with open(record_file, 'w') as file:
            file.write(rec)

        r = proc.parse_xml(xml_text=rec)
        xpproc.set_context(xdm_item=r)
        rwhen = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value()
        ruser = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()
        logging.info(f"new version[{record_file}] when[{rwhen}] user[{ruser}]")

        return "OK", rwhen
    
def rec_history(app: str, prof: str, nr: str):
    res = {
        "nr": nr,
        "history" : []
    }
    record_file = f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/record-{nr}.xml"  
    cur = version(record_file, app)
    res["history"].append(cur)
    
    hystery = []
    for record_file in glob.iglob(f"{settings.URL_DATA_APPS}/{app}/profiles/{prof}/records/history/record-{nr}.*.xml"): 
        ver = version(record_file, app) 
        hystery.append(ver)

    # https://favtutor.com/blogs/glob-python

    hystery.sort(key=operator.itemgetter('epoch'), reverse=True)
    # https://realpython.com/sort-python-dictionary/
    for ver in hystery:
        res["history"].append(ver)

    return res

def version(record_file, app):
    with PySaxonProcessor(license=False) as proc:
        xpproc = proc.new_xpath_processor()
        xpproc.declare_namespace('clariah','http://www.clariah.eu/')
        xpproc.set_context(file_name=record_file)
        when = xpproc.evaluate_single("string((/*:CMD/*:Header/*:MdCreationDate/@clariah:epoch,/*:CMD/*:Header/*:MdCreationDate,'unknown')[1])").get_string_value() 
        if '-' in when:
            utc_time = datetime.strptime(f"{when}T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ")
            when = math.floor((utc_time - datetime(1970, 1, 1)).total_seconds())
        else:
            when = int(when)
        timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime(when))            
        user = xpproc.evaluate_single(f"string((/*:CMD/*:Header/*:MdCreator,'{def_user(app)}')[1])").get_string_value()

        ver = {"epoch" :when, "user": user, "timestamp": timestamp }
        return ver
    

def getTime(epoch):
        time = datetime.fromtimestamp(int(epoch))        
        return time