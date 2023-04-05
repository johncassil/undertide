import unittest
from unittest.mock import patch
from src.util.secrets.aws_secrets_manager import UndertideAWSSecretsManager


class TestUndertideAWSSecretsManager(unittest.TestCase):
    def setUp(self):
        self.secrets_manager = UndertideAWSSecretsManager()

    @patch.object(UndertideAWSSecretsManager, "_create_client")
    def test_get_secret(self, mock_create_client):
        mock_client = mock_create_client.return_value
        expected_secret = {"username": "testuser", "password": "testpassword"}
        mock_client.get_secret_value.return_value = {
            "SecretString": '{"username": "testuser", "password": "testpassword"}'
        }
        secret = self.secrets_manager.get_secret("test-secret")
        self.assertEqual(secret, expected_secret)

    @patch.object(UndertideAWSSecretsManager, "_create_client")
    def test_get_secret_with_invalid_json(self, mock_create_client):
        mock_client = mock_create_client.return_value
        mock_client.get_secret_value.return_value = {"SecretString": "invalid json"}
        with self.assertRaises(ValueError):
            self.secrets_manager.get_secret("test-secret")
