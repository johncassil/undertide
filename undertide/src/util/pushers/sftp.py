import paramiko
import tenacity
from src.util.secrets import SecretManager


class UndertideSftp(paramiko.SFTPClient):
    def __init__(
        self,
        host: str,
        port: int = 22,
        creds_secret: str = None,
        username: str = None,
        password: str = None,
    ):
        """

        Args:
            host:
            port:
            creds_secret:
            username:
            password:
        """

        self.host = host
        self.port = port

        if creds_secret:
            sftp_creds = SecretManager().get_secret(
                secret_id=creds_secret, is_json=True
            )
            self.username = sftp_creds.get("username", None)
            self.password = sftp_creds.get("password", None)
        else:
            self.username = username
            self.password = password

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self.host, port=self.port, username=self.username, password=self.password
        )

        self.client = ssh.open_sftp()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        """"""

        if hasattr(self, "client") and self.client:
            self.client.close()
