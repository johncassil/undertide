import unittest
from unittest.mock import MagicMock, patch
from src.util.secrets.gcp_secrets_manager import UndertideGCPSecretsManager


class TestUndertideGCPSecretsManager(unittest.TestCase):
    def setUp(self):
        self.secret_manager = UndertideGCPSecretsManager(project_id="test_project")

    @patch("src.util.secrets.gcp_secrets_manager.secretmanager")
    def test_get_secret(self, mock_secretmanager):
        mock_secretmanager.SecretManagerServiceClient.return_value = MagicMock()
        this = mock_secretmanager.SecretManagerServiceClient()
        this.access_secret_version.return_value = MagicMock()
        this.access_secret_version().payload.data.decode.return_value = (
            '{"test_key": "test_value"}'
        )

        result = self.secret_manager.get_secret("test_secret")

        self.assertEqual(result, {"test_key": "test_value"})
