import os
import pyarrow as pa
import pyarrow.fs as pa_fs
import paramiko
import boto3
from google.cloud import storage
from src.util.secrets.secrets import UndertideSecretsManager
from src.logger import setup_logger

L = setup_logger()

class UndertideReportDeliverer():
    def __init__(self, local_file_path, delivery_method, delivery_secret_name, delivery_directory):
        self.local_file_path = local_file_path
        self.delivery_method = delivery_method
        self.delivery_secret_name = delivery_secret_name
        self.delivery_secret = self.get_delivery_secret()
        self.delivery_directory = delivery_directory
        if self.delivery_directory is None:
            self.delivery_directory = self.delivery_secret.get("delivery_directory", None)
        self.delivered_report = self.deliver_report()

    def get_delivery_secret(self):
        # Get the delivery secret from secrets manager
        secrets_manager = UndertideSecretsManager()
        delivery_secret = secrets_manager.get_secret(self.delivery_secret_name)
        return delivery_secret

    def deliver_report(self):
        if self.delivery_method == "sftp":
            self.delivered_report = self.deliver_report_sftp()
        elif self.delivery_method == "s3":
            self.delivered_report = self.deliver_report_s3()
        elif self.delivery_method == "gcs":
            self.delivered_report = self.deliver_report_gcs()
        else:
            raise ValueError(f"Unsupported delivery method {self.delivery_method}")
        return self.delivered_report

    def deliver_report_sftp(self):
        # Get the sftp credentials from the delivery secret
        sftp_host = self.delivery_secret.get("sftp", {}).get("host", None)
        if sftp_host is None:
            L.error(f"Missing sftp.host in delivery secret {self.delivery_secret_name}")
            raise ValueError(f"Missing sftp.host in delivery secret {self.delivery_secret_name}")
        sftp_username = self.delivery_secret.get("sftp", {}).get("username", None)
        if sftp_username is None:
            L.error(f"Missing sftp.username in delivery secret {self.delivery_secret_name}")
            raise ValueError(f"Missing sftp.username in delivery secret {self.delivery_secret_name}")
        sftp_password = self.delivery_secret.get("sftp", {}).get("password", None)
        if sftp_password is None:
            L.error(f"Missing sftp.password in delivery secret {self.delivery_secret_name}")
            raise ValueError(f"Missing sftp.password in delivery secret {self.delivery_secret_name}")
        sftp_port = self.delivery_secret.get("sftp", {}).get("port", 22)
        
        # Set up the sftp connection and transport
        transport = paramiko.Transport((sftp_host, sftp_port))
        transport.connect(username=sftp_username, password=sftp_password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Set the remote file path
        remote_file_path = os.path.join(self.delivery_directory, os.path.basename(self.cloud_file_path))
        
        # Write the file to sftp
        try:
            with pa.fs.File(self.local_file_path, 'rb') as file:
                sftp.putfo(file, remote_file_path)
        except Exception as e:
            L.error(f"Error uploading file {self.local_file_path} to SFTP server {sftp_host}")
            L.error(e)
            raise e
        
        # Close the sftp connection and transport
        sftp.close()
        transport.close()
        
        return remote_file_path

def deliver_report_gcs(self):
    """Uploads a local file to a Google Cloud Storage bucket"""

    # Get the gcs credentials from the delivery secret
    gcs_bucket = self.delivery_secret.get("gcs", {}).get("bucket", None)
    if gcs_bucket is None:
        L.error(f"Missing gcs.bucket in delivery secret {self.delivery_secret_name}")
        raise ValueError(f"Missing gcs.bucket in delivery secret {self.delivery_secret_name}")
    gcs_credentials = self.delivery_secret.get("gcs", {}).get("credentials", None)
    if gcs_credentials is None:
        L.info(f"Missing gcs.credentials in delivery secret {self.delivery_secret_name}. Proceeding without credentials.")
    
    # Create a client and get the bucket
    if gcs_credentials:
        client = storage.Client.from_service_account_info(gcs_credentials)
    else:
        client = storage.Client()

    bucket = client.get_bucket(gcs_bucket)

    # Create a blob object and upload the file to the bucket
    if self.delivery_directory:
        blob = bucket.blob(self.delivery_directory + "/" + self.local_file_path)
    else:
        blob = bucket.blob(self.local_file_path)

    try:
        blob.upload_from_filename(self.local_file_path)
    except Exception as e:
        L.error(f"Error uploading file {self.local_file_name} to GCS bucket: {gcs_bucket}")
        L.error(e)
        raise e

    # Return the name of the uploaded file in the bucket
    return blob.name

def deliver_report_s3(self):
    """Uploads a local file to an Amazon S3 bucket"""
    # Get the s3 credentials from the delivery secret
    s3_access_key = self.delivery_secret.get("s3", {}).get("aws_access_key_id", None)
    if s3_access_key is None:
        L.info(f"Missing s3.aws_access_key_id in delivery secret {self.delivery_secret_name}")
    s3_secret_key = self.delivery_secret.get("s3", {}).get("aws_secret_access_key", None)
    if s3_secret_key is None:
        L.info(f"Missing s3.aws_secret_access_key in delivery secret {self.delivery_secret_name}")
    s3_bucket = self.delivery_secret.get("s3", {}).get("bucket", None)
    if s3_bucket is None:
        L.error(f"Missing s3.bucket in delivery secret {self.delivery_secret_name}")
        raise ValueError(f"Missing s3.bucket in delivery secret {self.delivery_secret_name}")

    # Create an S3 client and upload the file to the bucket
    if s3_access_key and s3_secret_key:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
    else:
        s3 = boto3.resource('s3')
    
    if self.delivery_directory:
        file_name = self.delivery_directory + "/" + self.local_file_name
    else:
        file_name = self.local_file_name

    try:   
        s3.Bucket(s3_bucket).upload_file(self.local_file_name, file_name)
    except Exception as e:
        L.error(f"Error uploading file {self.local_file_name} to S3 bucket {s3_bucket}")
        L.error(e)
        raise e

    # Return the name of the uploaded file in the bucket
    return file_name
    
