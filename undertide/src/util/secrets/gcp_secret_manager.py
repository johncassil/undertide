import json
import os
import google.auth
from google.cloud import secretmanager
from src.logger import setup_logger

L = setup_logger()


class GCPSecretManager:
    """Object for interacting with Google Secret Manager

    Attributes:
        project_id (str): Project ID for GCP project to interact with.

    """

    def __init__(self, project_id=None):
        # Create the Secret Manager client.
        self.client = secretmanager.SecretManagerServiceClient()

        if not project_id:
            L.info("Getting project_id for SecretManager initialization.")
            project_id = self._get_current_project_id()

        self.project_id = project_id

    @staticmethod
    def _get_current_project_id():
        L.debug("Checking environment vars for GCP_PROJECT.")
        project_id = os.getenv("GCP_PROJECT")

        if not project_id:
            L.debug(
                "GCP_PROJECT not found in environment vars. Attempting to get project_id from google auth call."
            )
            _, project_id = google.auth.default()

        return project_id

    def _build_secret_resource_name(self, secret_id, version_id="latest"):
        """Builds resource name for secret.

        Args:
            secret_id (str): ID (name) of secret to retrieve.
            version_id (str): Version ID of secret to retrieve. Defaults to latest.

        Returns:
            (str): formatted resource name for secret ID.
        """

        return f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"

    # @staticmethod
    # def _get_tokens_from_secrets_manager(client=self.client):
    #     """Returns all valid tokens from the secrets manager secret.
    #     Secrets will be stored in the JSON format:
    #     {"token1":"expiration1","token2":"expiration2"}
    #     where expiration is a UTC datetime string like "2020-01-01 00:00:00"
    #     """
    #     secret = "API_TOKENS"
    #     name = f"projects/{self.project_id}/secrets/{secret}/versions/latest"
    #     response = client.access_secret_version(request={"name": name})
    #     tokens_json = json.loads(response.payload.data.decode("UTF-8"))
    #     return tokens_json
    
    def get_secret(self, secret_id, version_id="latest"):
        """Retrieves stored contents for secret in GCP Secret Manager.

        Args:
            secret_id (str): ID (name) of secret to retrieve.
            version_id (str): Version ID of secret to retrieve. Defaults to latest.
            is_json (bool): Flag specifying if secret is stored as json. If set to
            True then attempt will be made to load returned value to dictionary.

        Returns:
            (str or dict): Returns contents of stored secret as a string or dictionary.
        """

        L.info(
            "Attempting to retrieve secret {}:{} from secrets manager in project {}".format(
                secret_id, version_id, self.project_id
            )
        )

        # Access the secret version.
        response = self.client.access_secret_version(
            name=self._build_secret_resource_name(secret_id, version_id)
        )

        # Return the decoded payload
        L.info(
            "Reading secret {}:{} payload as json.".format(secret_id, version_id)
        )
        try:
            json_secret = json.loads(response.payload.data.decode("UTF-8"))
            
        except json.decoder.JSONDecodeError:
            raise ValueError("Secrets Manager secret %s is not valid JSON." % secret_id)


        return json_secret
