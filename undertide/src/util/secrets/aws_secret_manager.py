import json
import os
import boto3
from botocore.exceptions import ClientError

from src.logger import setup_logger

L = setup_logger()


class AWSSecretManager:
    """
    Object for interacting with AWS Secrets Manager.
    Ensures that we can get AWS secrets in JSON from the AWS Secrets Manager.
    """
    def __init__(self, region_name=None, access_key=None, secret_key=None):
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION')
        self.access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.client = self._create_client()

    def _create_client(self):
        kwargs = {
            'region_name': self.region_name
        }
        if self.access_key and self.secret_key:
            kwargs['aws_access_key_id'] = self.access_key
            kwargs['aws_secret_access_key'] = self.secret_key
        return boto3.client('secretsmanager', **kwargs)

    def get_secret(self, secret_name):
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                raise ValueError("Secrets Manager secret %s not found." % secret_name)
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                raise ValueError("Invalid request for Secrets Manager secret %s." % secret_name)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                raise ValueError("Invalid parameter for Secrets Manager secret %s." % secret_name)
            else:
                raise e
        else:
            if 'SecretString' in response:
                L.info(
                    "Reading secret {} payload as json.".format(secret_name)
                )
                try: 
                    json_secret = json.loads(response['SecretString'])
                except json.decoder.JSONDecodeError:
                    raise ValueError("Secrets Manager secret %s is not valid JSON." % secret_name)

                return json_secret