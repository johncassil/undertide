import os
import pytest
import json
from unittest.mock import patch
from src.util.gcp_secret_manager import SecretManager

os.environ["GCP_PROJECT"] = "TEST"


@pytest.fixture()
def secret_string_value():
    return "super_secret_token"


@pytest.fixture()
def secret_json_value():
    return '{"user": "me", "password": "default", "uri": "here", "port": 80}'


@patch("src.util.secrets.secretmanager.SecretManagerServiceClient")
def test_get_secret_string(mock_smc, secret_string_value):
    mock_smc.return_value.access_secret_version.return_value.payload.data = (
        secret_string_value.encode("UTF-8")
    )

    client = secrets.SecretManager("test")
    secret_string = client.get_secret(secret_id="test")

    assert secret_string == secret_string_value


@patch("src.util.secrets.secretmanager.SecretManagerServiceClient")
def test_get_secret_json(mock_smc, secret_json_value):
    mock_smc.return_value.access_secret_version.return_value.payload.data = (
        secret_json_value.encode("UTF-8")
    )

    client = secrets.SecretManager("test")
    secret_dict = client.get_secret(secret_id="test", is_json=True)

    assert json.dumps(secret_dict) == secret_json_value


@patch("google.auth.default")
def test_get_project(mock_auth):
    del os.environ["GCP_PROJECT"]

    mock_auth.return_value = ("", "test-project")

    project_id = secrets.SecretManager()._get_current_project_id()

    assert project_id == "test-project"
