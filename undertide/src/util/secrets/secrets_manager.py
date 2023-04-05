import os
import time

# import datetime
from src.util.secrets.aws_secrets_manager import UndertideAWSSecretsManager
from src.util.secrets.gcp_secrets_manager import UndertideGCPSecretsManager


class UndertideSecretsManager:
    def __init__(self):
        cloud_provider = os.environ.get("CLOUD_PROVIDER")
        if cloud_provider == "AWS":
            self.secret_manager = UndertideAWSSecretsManager()
        elif cloud_provider == "GCP":
            self.secret_manager = UndertideGCPSecretsManager()
        else:
            raise ValueError(
                "Invalid CLOUD_PROVIDER environment variable value. Please set "
                "it to 'AWS' or 'GCP'."
            )

        self.cache = {}
        # self.token_cache = {}

    def get_secret(self, secret_name, max_age=86400):
        now = time.time()
        if secret_name in self.cache:
            value, timestamp = self.cache[secret_name]
            if now - timestamp <= max_age:
                return value
        value = self.secret_manager.get_secret(secret_name)
        self.cache[secret_name] = (value, now)
        return value


# def check_token(self, token):
#     now = datetime.datetime.utcnow()
#     expiration = self.tokens.get(token)
#     if expiration is not None:
#         expiration = datetime.datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S")
#     if expiration is not None and expiration > now:
#         return True
#     else:
#         self.tokens = self._get_tokens_from_secrets_manager(self.client, self.name)
#         expiration = self.tokens.get(token)
#         return expiration is not None and expiration > now
