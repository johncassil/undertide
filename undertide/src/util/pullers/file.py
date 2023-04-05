import os
from google.cloud import storage
import boto3


class CloudFileRetriever:
    def __init__(self):
        self.cloud_provider = os.environ.get("CLOUD_PROVIDER")
        if self.cloud_provider == "gcs":
            self.client = storage.Client()
        elif self.cloud_provider == "s3":
            self.client = boto3.client("s3")
        else:
            raise ValueError(f"Unknown cloud provider: {self.cloud_provider}")

        self.file_cache = {}

    def get_file(self, bucket_name, file_name):
        cache_key = f"{bucket_name}/{file_name}"
        if cache_key in self.file_cache:
            return self.file_cache[cache_key]

        if self.cloud_provider == "gcs":
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(file_name)
            file_content = blob.download_as_string()
        elif self.cloud_provider == "s3":
            obj = self.client.get_object(Bucket=bucket_name, Key=file_name)
            file_content = obj["Body"].read()
        else:
            raise ValueError(f"Unknown cloud provider: {self.cloud_provider}")

        self.file_cache[cache_key] = file_content
        return file_content
