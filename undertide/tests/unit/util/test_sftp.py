import os
from google.auth import _default
from unittest import TestCase, mock
from src.util import sftp


class UndertideSftpTest(TestCase):
    def setUp(self):
        self.service_account_file = os.path.join(
            os.path.dirname(__file__), "../data/service_account.json"
        )

        test_credentials, test_project_id = _default.load_credentials_from_file(
            self.service_account_file,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        self.secret_json_value = '{"username": "me", "password": "default"}'

        with mock.patch("paramiko.SSHClient") as m_c, mock.patch(
            "src.util.secrets.secretmanager.SecretManagerServiceClient"
        ) as m_sc, mock.patch(
            "google.auth._default._get_gcloud_sdk_credentials"
        ) as mock_get:
            mock_get.return_value = (test_credentials, test_project_id)
            client = mock.Mock()
            m_c.open_sftp.return_value = client

            m_sc.return_value.access_secret_version.return_value.payload.data = (
                self.secret_json_value.encode("UTF-8")
            )

            self.sftp_obj = sftp.UndertideSftp(
                host="10.0.0.1", port=22, username="testuser", password="1234"
            )

            self.sftp_obj_w_scrt = sftp.UndertideSftp(
                host="10.0.0.1", port=22, creds_secret="test_sftp_secret"
            )

    def test_cleanup(self):
        with mock.patch("paramiko.Transport") as m_t, mock.patch(
            "paramiko.SFTPClient"
        ) as m_c:
            self.sftp_obj.cleanup()
