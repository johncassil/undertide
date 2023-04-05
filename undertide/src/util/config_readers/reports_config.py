import os
import boto3
import yaml

from google.cloud import storage
from src.logger import setup_logger

L = setup_logger()


class UndertideCloudFileRetriever:
    def __init__(self):
        self.cloud_provider = os.environ.get("CLOUD_PROVIDER")
        if self.cloud_provider == "gcs":
            self.client = storage.Client()
        elif self.cloud_provider == "s3":
            self.client = boto3.client("s3")
        else:
            raise ValueError(f"Unknown cloud provider: {self.cloud_provider}")
        self.bucket = os.environ.get("REPORTS_CONFIG_BUCKET")

    def get_yaml_file(self, file_name):
        return self._get_file(self.bucket, file_name, "yaml")

    def get_sql_file(self, file_name):
        return self._get_file(self.bucket, file_name, "sql")

    def get_py_file(self, file_name):
        return self._get_file(self.bucket, file_name, "py")

    def _get_file(self, file_name, file_type):
        L.info(
            f"Getting {file_type} file {file_name} from"
            f" {self.cloud_provider} bucket {self.bucket}"
        )
        if self.cloud_provider == "gcs":
            try:
                bucket = self.client.get_bucket(self.bucket)
                blob = bucket.blob(file_name)
                file_content = blob.download_as_string().decode("utf-8")
            except Exception as e:
                L.error(
                    f"Error getting file {file_name} from bucket {self.bucket}: {e}"
                )
                raise e
        elif self.cloud_provider == "s3":
            try:
                obj = self.client.get_object(Bucket=self.bucket, Key=file_name)
                file_content = obj["Body"].read().decode("utf-8")
            except Exception as e:
                L.error(
                    f"Error getting file {file_name} from bucket {self.bucket}: {e}"
                )
                raise e
        else:
            raise ValueError(f"Unknown cloud provider: {self.cloud_provider}")

        if file_type == "yaml":
            file_content = yaml.safe_load(file_content)
        elif file_type == "sql":
            file_content = file_content.strip()
        elif file_type == "py":
            file_content = file_content
        else:
            raise ValueError(f"Unknown file type: {file_type}")

        return file_content


class UndertideYamlConfig:
    def __init__(self, yaml_file_contents):
        self.contents = yaml_file_contents
        self.data_pull_method = self.contents.get("data_pull_method")
        self.compression = self.contents.get("compression")
        self.file_format = self.contents.get("file_format", "csv")
        self.sql_file = self.contents.get("sql_file")
        self.py_file = self.contents.get("py_file")
        self.bucket = self.contents.get("bucket")
        self.file_reader = UndertideCloudFileRetriever()
        self.report_type = self._get_report_type()
        self.sql = self._get_sql()
        self.py = self._get_py()

    def _get_report_type(self):
        if self.sql_file:
            return "sql"
        elif self.py_file:
            # ensure that self.data_pull_method is either gcs or s3
            if self.data_pull_method not in ["gcs", "s3"]:
                raise ValueError(
                    f"Invalid data_pull_method: {self.data_pull_method}"
                    f" for data pull method: {self.data_pull_method}"
                )
            return "py"
        else:
            return None

    def _get_sql(self):
        if self.report_type == "sql":
            return self.file_reader.get_sql_file(self.sql_file)
        else:
            return None

    def _get_py(self):
        if self.report_type == "py":
            return self.file_reader.get_py_file(self.py_file)
        else:
            return None
