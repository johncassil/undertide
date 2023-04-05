import os
import boto3
import pandas as pd
from google.cloud import storage
from src.logger import setup_logger
from datetime import datetime

L = setup_logger()

class UndertidePyFileFinder:
    def __init__(self, data_pull_method: str, report_name: str, bucket: str, file_format: str, dry_run: bool, user_function_str: str):
        self.user_function = {}
        exec(user_function_str, self.user_function)
        self.bucket_type = data_pull_method
        self.bucket = bucket
        self.file_format = file_format
        self.report_name = report_name
        if self.dry_run:
            self.file_name = f"DRY_RUN_{self.report_name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        else:
            self.file_name = f"{self.report_name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        self.local_file_path = self.get_file()

    def get_file(self):
        L.info(f"Getting file for {self.report_name} from {self.bucket_type} bucket {self.bucket}")

        if self.bucket_type == 's3':
            # Download file from S3
            try:
                client = boto3.client('s3')
            except Exception as e:
                L.error(f"Error getting S3 client: {e}")
                raise e
            
            try:
                file_path = self.user_function['find_file'](self.bucket)
                file_extension = file_path.split('.')[-1]
                downloaded_file = f"{self.file_name}.{file_extension}"
                client.download_file(self.bucket, file_path, downloaded_file)
            except Exception as e:
                L.error(f"Error getting file: {e}")
                raise e

        elif self.bucket_type == 'gcs':
            # Download file from GCS
            try:
                client = storage.Client()
            except Exception as e:
                L.error(f"Error getting GCS client: {e}")
                raise e

            try:
                bucket = client.get_bucket(self.bucket)
                file_path = self.user_function['find_file'](self.bucket)
                file_extension = file_path.split('.')[-1]
                downloaded_file = f"{self.file_name}.{file_extension}"
                blob = bucket.blob(file_path)
                blob.download_to_filename(downloaded_file)
            except Exception as e:
                L.error(f"Error getting file: {e}")
                raise e

        else:
            raise ValueError(f"Unknown bucket type {self.bucket_type}")
        
        # If format extension matches self.file_format, return the file name
        if self.file_format == file_extension:
            self.file_name = downloaded_file
        else:
            self.file_name = self.transform_file(downloaded_file, self.file_format, file_extension)
        
        return self.file_name

    def transform_file(self, downloaded_file, file_format, file_extension):
        # transform the file to the desired format
        # return the new file name
        if file_extension == 'csv':
            #read the csv file
            df = pd.read_csv(downloaded_file)
        elif file_extension == 'parquet':
            #read the parquet file
            df = pd.read_parquet(downloaded_file)
        elif file_extension == 'txt':
            #read the txt file
            df = pd.read_csv(downloaded_file, sep='\t')
        elif file_extension == 'avro':
            #read the avro file
            df = pd.read_avro(downloaded_file)
        else:
            raise ValueError(f"File extension: {file_extension} is not supported yet!")
        
        file_name = f"{self.file_name}.{file_format}"

        if file_format == 'csv':
            #write the csv file
            df.to_csv(file_name, index=False)
        elif file_format == 'parquet':
            #write the parquet file
            df.to_parquet(file_name, index=False)
        elif file_format == 'txt':
            #write the txt file
            df.to_csv(file_name, index=False, sep='\t')
        elif file_format == 'avro':
            #write the avro file
            df.to_avro(file_name, index=False)
        else:
            raise ValueError(f"File format: {file_format} is not supported yet!")
        
        return file_name
