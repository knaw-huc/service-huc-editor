import os
from typing import Optional, Annotated

from fastapi import Depends
from saxonche import PySaxonProcessor, PyXPathProcessor, PyXdmNode, PyXslt30Processor, PyXsltExecutable, PyXdmValue

from src.commons import settings, convert_toml_to_xml


class NotInitializedException(Exception):
    """
    Not yet initialized
    """


class RecordMetadata:
    """
    Saxon based XSLT parser for retrieving metadata from a record
    """
    saxon: PySaxonProcessor
    xpath_processor: PyXPathProcessor
    records_location: str
    record: Optional[PyXdmNode]

    def __init__(self, processor: PySaxonProcessor, records_location: str):
        self.saxon = processor
        self.xpath_processor = processor.new_xpath_processor()
        self.xpath_processor.set_cwd(os.getcwd())
        self.xpath_processor.declare_namespace('clariah', 'http://www.clariah.eu/')
        self.xpath_processor.declare_namespace('cmd', 'http://www.clarin.eu/cmd/')
        self.records_location = records_location


    def set_record(self, record):
        """
        Set the record to work with
        :param record:
        :return:
        """
        with open(f"{self.records_location}/record-{record}.xml", "r") as f:
            self.record = self.saxon.parse_xml(xml_text=f.read())
            self.xpath_processor.set_context(xdm_item=self.record)


    def parse_single(self, xpath_expression: str):
        """
        Get a single value from the record
        :param xpath_expression:
        :return:
        """
        if self.record is None:
            raise NotInitializedException()
        return self.xpath_processor.evaluate_single(xpath_expression).get_string_value()



class StylesheetProcessor:
    """
    Processor for XSLT stylesheets.
    """
    saxon: PySaxonProcessor
    xslt_processor: PyXslt30Processor
    stylesheet: PyXsltExecutable
    app: str

    def __init__(self, processor: PySaxonProcessor, app: str):
        self.saxon = processor
        self.xslt_processor = processor.new_xslt30_processor()
        self.xslt_processor.set_cwd(os.getcwd())
        self.app = app


    def set_stylesheet(self, stylesheet: str):
        """
        Load stylesheet and set default parameters
        :param stylesheet:
        :return:
        """
        self.stylesheet = self.xslt_processor.compile_stylesheet(stylesheet_file=f"{settings.xslt_dir}/{stylesheet}.xsl")
        # TODO: this should be able to run only once? Maybe cache the xml config
        convert_toml_to_xml(f"{settings.URL_DATA_APPS}/{self.app}/config.toml",f"{settings.URL_DATA_APPS}/{self.app}/config.xml")
        config = self.saxon.parse_xml(xml_file_name=f"{settings.URL_DATA_APPS}/{self.app}/config.xml")

        # Set default parameters
        self.set_parameter("cwd", os.getcwd())
        self.set_parameter("base", settings.url_base)
        self.set_parameter("app", self.app)
        self.set_parameter("config", config)


    def set_parameter(self, key: str, value: str | PyXdmValue):
        """
        Set parameter
        :param key:
        :param value:
        :return:
        """
        if isinstance(value, str):
            self.stylesheet.set_parameter(key, self.saxon.make_string_value(value))
        else:
            self.stylesheet.set_parameter(key, value)


    def apply(self, record: Optional[str] = None, profile: Optional[str] = None):
        """
        Apply the stylesheet to a null value, a record or a profile
        :return:
        """
        if record is not None:
            record_file = f"{settings.URL_DATA_APPS}/{self.app}/record-{record}.xml"
            rec = self.saxon.parse_xml(xml_uri=record_file)
            return self.stylesheet.transform_to_string(xdm_node=rec)
        if profile is not None:
            profile_path = f"{settings.URL_DATA_APPS}/{self.app}/profiles/{profile}"
            prof = self.saxon.parse_xml(xml_file_name=f"{profile_path}/{profile}.xml")
            return self.stylesheet.transform_to_string(xdm_node=prof)

        null = self.saxon.parse_xml(xml_text="<null/>")
        return self.stylesheet.transform_to_string(xdm_node=null)

    def main(self):
        """
        Call the main template of the stylesheet
        :return:
        """
        return self.stylesheet.call_template_returning_string("main")


def get_saxon_processor():
    """
    Dependency function for getting a saxon processor
    :return:
    """
    with PySaxonProcessor(license=False) as saxon_processor:
        yield saxon_processor

SaxonProcessorDep = Annotated[PySaxonProcessor, Depends(get_saxon_processor)]


def get_xslt_processor(app: str, saxon: SaxonProcessorDep) -> StylesheetProcessor:
    """
    Dependency function for getting a xslt processor
    :param app:
    :param saxon:
    :return:
    """
    return StylesheetProcessor(saxon, app)

StylesheetProcessorDep = Annotated[StylesheetProcessor, Depends(get_xslt_processor)]


class StylesheetDep:
    """
    Dependency function for getting a saxon processor. Allows specifying the name of the stylesheet
    to load.
    """
    stylesheet_name: str

    def __init__(self, stylesheet_name: str):
        self.stylesheet_name = stylesheet_name

    def __call__(self, app: str, saxon: SaxonProcessorDep):
        processor = StylesheetProcessor(saxon, app)
        processor.set_stylesheet(self.stylesheet_name)
        return processor
