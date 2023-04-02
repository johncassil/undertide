from google.cloud import storage
from google.auth import default
from google.auth.transport.requests import Request
import google.auth.iam as iam
from google.oauth2 import service_account
import datetime

from src.logger import setup_logger
from typing import Tuple


L = setup_logger()

GCS_CLIENT = storage.Client()
DEFAULT_SIGNED_LINK_EXPIRATION = 168


def upload_files_to_gcs(
    bucket: str,
    local_path: str,
    gcs_path: str,
) -> None:
    """Upload a file from a local path to GCS."""

    L.info(f"Uploading file from {local_path} to {gcs_path}")

    bucket = GCS_CLIENT.bucket(bucket)
    json_bag_file = bucket.blob(gcs_path)
    json_bag_file.upload_from_filename(local_path)

    L.success(f"File has been uploaded from {local_path} to {gcs_path}")

    return


def generate_signed_link(
    bucket: str,
    file_name: str,
    signed_link_expiration_hrs: int = DEFAULT_SIGNED_LINK_EXPIRATION,
) -> Tuple[str, str]:
    # Generate a v4 signed URL for downloading a blob.
    bucket = GCS_CLIENT.bucket(bucket)
    blob = bucket.blob(file_name)

    L.debug("Attempting to generate signed link.")

    credentials, project = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    credentials.refresh(Request())

    L.debug("Creating Signer object.")

    signer = iam.Signer(
        request=Request(),
        credentials=credentials,
        service_account_email=credentials.service_account_email,
    )

    L.debug("Attempting to generate signing credentials.")

    signing_credentials = service_account.IDTokenCredentials(
        signer=signer,
        token_uri="https://www.googleapis.com/oauth2/v4/token",
        target_audience="",
        service_account_email=credentials.service_account_email,
    )

    L.debug("Generating signed url link.")

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(hours=signed_link_expiration_hrs),
        # Allow GET requests using this URL.
        method="GET",
        credentials=signing_credentials,
    )

    return url, project
