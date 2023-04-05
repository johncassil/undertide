import boto3
import pandas as pd
from google.cloud import storage
from src.logger import setup_logger
from datetime import datetime

L = setup_logger()

# Define a placeholder function for find_file() that will be replaced by the user's function
def find_file(client, bucket):
    L.error(f"find_file() function not defined by the user in the py file.{client} and {bucket} were given ")
    raise NotImplementedError("find_file() function not defined by the user in the py file.")

class UndertidePyFileFinder:
    def __init__(
        self,
        data_pull_method: str,
        report_name: str,
        bucket: str,
        file_format: str,
        dry_run: bool,
        user_function_str: str,
    ):
        self.user_function_str = user_function_str
        self.bucket_type = data_pull_method
        self.bucket = bucket
        self.file_format = file_format
        self.report_name = report_name
        self.dry_run = dry_run
        if self.dry_run:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.file_name = f"DRY_RUN_{self.report_name}_{timestamp}"
        else:
            self.file_name = (
                f"{self.report_name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
    

    def get_file(self):
        L.info(
            f"Getting file for {self.report_name} from {self.bucket_type} "
            f"bucket {self.bucket}"
        )

        if self.bucket_type == "s3":
            # Download file from S3
            try:
                client = boto3.client("s3")
            except Exception as e:
                L.error(f"Error getting S3 client: {e}")
                raise e

            try:
                L.info(f"The following user defined function was given: {self.user_function_str}")
                exec(self.user_function_str, globals())
                file_path = find_file(client, self.bucket)
                file_extension = file_path.split(".")[-1]
                downloaded_file = f"{self.file_name}.{file_extension}"
                client.download_file(self.bucket, file_path, downloaded_file)
            except Exception as e:
                L.error(f"Error getting file: {e}")
                raise e

        elif self.bucket_type == "gcs":
            # Download file from GCS
            try:
                client = storage.Client()
            except Exception as e:
                L.error(f"Error getting GCS client: {e}")
                raise e

            try:
                L.info(f"The following user defined function was given: {self.user_function_str}")
                exec(self.user_function_str, globals())
                file_path = find_file(client, self.bucket)
                file_extension = file_path.split(".")[-1]
                downloaded_file = f"{self.file_name}.{file_extension}"
                bucket = client.bucket(self.bucket)
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
            self.file_name = self.transform_file(
                downloaded_file, self.file_format, file_extension
            )

        return self.file_name

    def transform_file(self, downloaded_file, file_format, file_extension):
        # transform the file to the desired format
        # return the new file name
        if file_extension == "csv":
            # read the csv file
            df = pd.read_csv(downloaded_file)
        elif file_extension == "parquet":
            # read the parquet file
            df = pd.read_parquet(downloaded_file)
        elif file_extension == "txt":
            # read the txt file
            df = pd.read_csv(downloaded_file, sep="\t")
        elif file_extension == "avro":
            # read the avro file
            df = pd.read_avro(downloaded_file)
        else:
            raise ValueError(f"File extension: {file_extension} is not supported yet!")

        file_name = f"{self.file_name}.{file_format}"

        if file_format == "csv":
            # write the csv file
            df.to_csv(file_name, index=False)
        elif file_format == "parquet":
            # write the parquet file
            df.to_parquet(file_name, index=False)
        elif file_format == "txt":
            # write the txt file
            df.to_csv(file_name, index=False, sep="\t")
        elif file_format == "avro":
            # write the avro file
            df.to_avro(file_name, index=False)
        else:
            raise ValueError(f"File format: {file_format} is not supported yet!")

        return file_name
