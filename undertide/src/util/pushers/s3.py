import boto3
from src.util.gcp_secret_manager import SecretManager


class UndertideS3:
    def __init__(self, creds_secret: str):
        """

        Args:
            bucket_name:
            creds_secret:
        """

        self.creds_secret = creds_secret

        self.s3_creds = SecretManager().get_secret(
            secret_id=self.creds_secret, is_json=True
        )
        self.bucket_name = self.s3_creds.get("s3_bucket", None)
        self.access_key_id = self.s3_creds.get("access_key_id", None)
        self.secret_access_key = self.s3_creds.get("secret_access_key", None)

        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
        )
