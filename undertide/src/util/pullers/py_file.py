import os
import boto3
from google.cloud import storage
from src.logger import setup_logger
from datetime import datetime

L = setup_logger()

class UndertidePyFileFinder:
    def __init__(self, report_name: str, bucket: str, user_function_str: str):
        self.user_function = {}
        exec(user_function_str, self.user_function)
        self.cloud_provider = os.environ.get('CLOUD_PROVIDER')
        self.bucket = bucket
        self.report_name = report_name
        self.file_name = f"{self.report_name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        self.local_file_path = self.get_file()

    def get_file(self):
        clients = {
            'gcp': storage.Client(),
            'aws': boto3.client('s3')
        }
        client = clients.get(self.cloud_provider)
        if not client:
            raise ValueError(f"Unknown cloud provider: {self.cloud_provider}")

        L.info(f"Getting files for {self.report_name} from {self.cloud_provider} bucket {self.bucket}")
        try:
            if self.cloud_provider == 'gcp':
                # Download file from GCS
                bucket = client.get_bucket(self.bucket)
                file_path = self.user_function['find_file'](self.bucket)
                blob = bucket.blob(file_path)
                blob.download_to_filename(self.file_name)
            elif self.cloud_provider == 'aws':
                # Download file from S3
                file_path = self.user_function['find_file'](self.bucket)
                client.download_file(self.bucket, file_path, self.file_name)
            return self.file_name
        except Exception as e:
            L.error(f"Error getting file: {e}")
            raise e
