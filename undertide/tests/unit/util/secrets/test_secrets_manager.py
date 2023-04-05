import os
import unittest
from unittest.mock import MagicMock, patch

from src.util.secrets.aws_secrets_manager import UndertideAWSSecretsManager
from src.util.secrets.gcp_secrets_manager import UndertideGCPSecretsManager
from src.util.secrets.secrets_manager import UndertideSecretsManager


class TestUndertideSecretsManager(unittest.TestCase):
    @patch.dict(os.environ, {"CLOUD_PROVIDER": "aws"})
    def test_get_secret_aws(self):
        mock_secret_manager = MagicMock(spec=UndertideAWSSecretsManager)
        mock_secret_manager.get_secret.return_value = "test-secret-value"

        with patch(
            "src.util.secrets.secrets_manager.UndertideAWSSecretsManager",
            return_value=mock_secret_manager,
        ):
            secrets_manager = UndertideSecretsManager()
            self.assertEqual(
                secrets_manager.get_secret("test-secret"), "test-secret-value"
            )

    @patch.dict(os.environ, {"CLOUD_PROVIDER": "gcp"})
    def test_get_secret_gcp(self):
        mock_secret_manager = MagicMock(spec=UndertideGCPSecretsManager)
        mock_secret_manager.get_secret.return_value = "test-secret-value"

        with patch(
            "src.util.secrets.secrets_manager.UndertideGCPSecretsManager",
            return_value=mock_secret_manager,
        ):
            secrets_manager = UndertideSecretsManager()
            self.assertEqual(
                secrets_manager.get_secret("test-secret"), "test-secret-value"
            )
