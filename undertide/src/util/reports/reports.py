import json
from jinja2 import Template
from src.logger import setup_logger
from util.config_readers.reports_config import UndertideCloudFileRetriever, UndertideYamlConfig
from util.pullers.report_generator import UndertideSqlReportGenerator
from util.writers.report_writer import UndertideReportWriter
from util.pushers.report_deliverer import UndertideReportDeliverer
from util.pullers.py_file import UndertidePyFileFinder

L = setup_logger()

class UndertideReport():
    def __init__(self, report_name, report_config_jinja, delivery_method, delivery_secret_name, file_format, compression, delivery_directory):
        self.report_name = report_name
        self.report_config_jinja = report_config_jinja
        self.delivery_method = delivery_method
        self.delivery_secret_name = delivery_secret_name
        self.file_format = file_format
        self.compression = compression
        self.delivery_directory = delivery_directory
        self.report_config = self.get_report_config()
        if self.delivery_directory is None:
            self.delivery_directory = self.report_config.delivery_directory
        self.local_file_path = self.build_report()
        self.delivered_report = self.deliver_report()

    def get_report_config(self):
        # Get the report config from the bucket
        config_reader = UndertideCloudFileRetriever()
        L.info(f"Getting report config for {self.report_name}")
        report_config_file_contents = config_reader.get_yaml_file(f"reports/{self.report_name}")
        config = UndertideYamlConfig(report_config_file_contents)
        return config
        

    def build_report(self):
        if self.report_config.report_type == "sql":
            report_data = self.build_sql_report()
            local_file_path = self.write_report(report_data)
            return local_file_path
        elif self.report_config.report_type == "py":
            local_file_path = self.build_py_report()
            return local_file_path
        else:
            raise ValueError(f"Unknown report type {self.report_config.report_type}")


    def build_sql_report(self):
        L.info(f"Building report {self.report_name}")
        report_generator = UndertideSqlReportGenerator(self.report_config.data_pull_method)
        L.info(f"Replacing JINJA variables in sql query with {self.report_config_jinja}")
        sql_template = Template(self.report_config.sql)
        jinja_args = json.loads(self.report_config_jinja)
        sql_query = sql_template.render(jinja_args)
        report_data = report_generator.get_report_data(sql_query)
        return report_data

    def write_report(self, report_data):
        report_writer = UndertideReportWriter(report_data, self.file_format, self.report_name, self.compression, self.delivery_directory)
        report_writer.write_report()
        return report_writer.local_file_path

    def build_py_report(self):
        user_function_str = str(self.report_config.py['code'])
        # pass this to a class that will find the file, ensure that it only matches one file, 
        # and then download the file locally and rename it to the report name and return the local file name
        # note, this does not change the base data format.  That would need to be done by going upstream.  
        # This is just a shim in order to use files that another process has already created.
        local_file_path = UndertidePyFileFinder(self.report_name, self.report_config.bucket, user_function_str)
        return local_file_path

    def deliver_report(self):
        delivered_report = UndertideReportDeliverer(self.local_file_path, self.delivery_method, self.delivery_secret_name, self.delivery_directory)
        return delivered_report

    def run(self):
        self.get_report_config()
        self.build_report()
        self.compress_report()
        self.upload_report()
        self.deliver_report()