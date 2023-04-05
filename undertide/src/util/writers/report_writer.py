import os
import gzip
import bz2
import zipfile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
from google.cloud import storage
from datetime import datetime
from src.logger import setup_logger

L = setup_logger()


class UndertideReportWriter:
    def __init__(
        self,
        report_data: pd.DataFrame,
        file_format: str,
        report_name: str,
        compression: str,
        dry_run: bool,
    ):
        self.report_data = report_data
        self.file_format = file_format
        self.report_name = report_name
        self.compression = compression
        self.bucket_name = os.getenv("REPORTS_ARCHIVE_BUCKET")
        self.dry_run = dry_run
        self.client = None
        if self.dry_run:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            self.file_name = f"DRY_RUN_{self.report_name}_{timestamp}"
        else:
            self.file_name = (
                f"{self.report_name}_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
            )
        self.local_file_path = f"{self.file_name}.{self.file_format}"
        self.compressed_file_path = self.local_file_path


    def write_report(self):
        L.info(f"Writing report {self.report_name} to {self.local_file_path}")
        if self.file_format == "csv":
            self.write_csv_report()
        elif self.file_format == "txt":
            self.write_txt_report()
        elif self.file_format == "parquet":
            self.write_parquet_report()
        elif self.file_format == "avro":
            self.write_avro_report()
        else:
            raise ValueError(f"Unsupported file type: {self.file_format}")

        if self.compression:
            self.compress_report()

        self.upload_to_cloud_storage_archive()

    def write_csv_report(self):
        # Write the Pandas DataFrame to a CSV file
        self.report_data.to_csv(self.local_file_path, index=False)

    def write_parquet_report(self):
        # Write the Pandas DataFrame to a Parquet file
        table = pa.Table.from_pandas(self.report_data)
        pq.write_table(table, self.local_file_path)

    def write_txt_report(self):
        # Write the Pandas DataFrame to a TXT file
        self.report_data.to_csv(self.local_file_path, index=False, sep="\t")

    def write_avro_report(self):
        # Write the Pandas DataFrame to an Avro file
        table = pa.Table.from_pandas(self.report_data)
        with open(self.local_file_path, "wb") as avro_file:
            writer = pa.ipc.new_file(avro_file, table.schema)
            writer.write_table(table)
            writer.close()

    def compress_report(self):
        L.info(f"Compressing {self.local_file_path} with {self.compression}")
        if self.compression == "gzip":
            # Compress the file with gzip
            self.compressed_file_path = f"{self.local_file_path}.gz"
            with open(self.local_file_path, "rb") as f_in:
                with gzip.open(self.compressed_file_path, "wb") as f_out:
                    f_out.writelines(f_in)
            # Remove the original uncompressed file
            os.remove(self.local_file_path)

        elif self.compression == "bz2":
            # Compress the file with bzip2
            self.compressed_file_path = f"{self.local_file_path}.bz2"
            with open(self.local_file_path, "rb") as f_in:
                with bz2.open(self.compressed_file_path, "wb") as f_out:
                    f_out.writelines(f_in)
            # Remove the original uncompressed file
            os.remove(self.local_file_path)

        elif self.compression == "zip":
            # Compress the file with zip
            self.compressed_file_path = f"{self.local_file_path}.zip"
            with zipfile.ZipFile(self.compressed_file_path, "w") as zip_file:
                zip_file.write(self.local_file_path)
            # Remove the original uncompressed file
            os.remove(self.local_file_path)

        else:
            raise ValueError(f"Unsupported compression type: {self.compression}")

    def upload_to_cloud_storage_archive(self):
        cloud_env = os.getenv("CLOUD_PROVIDER")

                
        if cloud_env == "gcp":
            L.info("Creating GCS client")
            if self.client is None:
                try:
                    self.client = storage.Client()
                except Exception as e:
                    L.error(f"Error creating GCS client: {e}")
                    raise e
            try:
                L.info(f"Uploading {self.compressed_file_path} to {self.bucket_name}")
                bucket = self.client.get_bucket(self.bucket_name)
                blob = bucket.blob(f"sent_reports/{self.compressed_file_path}")
                blob.upload_from_filename(self.compressed_file_path)
            except Exception as e:
                L.error(f"Error uploading file to GCS: {e}")
                raise e
                         
        elif cloud_env == "aws":
            L.info("Creating S3 client")
            if self.client is None:
                try:
                    self.client = boto3.client("s3")
                except Exception as e:
                    L.error(f"Error creating S3 client: {e}")
                    raise e
            try:
                L.info(f"Uploading {self.compressed_file_path} to {self.bucket_name}")
                self.client.upload_file(
                    self.compressed_file_path, self.bucket_name, f"sent_reports/{self.compressed_file_path}"
                )
            except Exception as e:
                L.error(f"Error uploading file to S3: {e}")
                raise e

        else:
            raise ValueError(f"Unsupported cloud provider: {cloud_env}")


