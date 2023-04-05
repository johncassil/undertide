import click
import json
from src.logger import setup_logger
from src.util.reports.reports import UndertideReport
from src.util.secrets.secrets import UndertideSecretsManager
from src.util.parse_config import parse_callable_config, parse_config

L = setup_logger()

@click.command()
@click.option(
    "--report_name",
    required=True,
    help="(string) The configuration for reports are stored in a bucket that you specify, and this is the name/path of the yaml file that contains the configuration for the report, for example, what data pull method to use, which sql file to use, or what logic to use to pull the file from a bucket (e.g. glob pattern, file name, etc). ",
)

@click.option(
    "--report_config_jinja",
    help="(stringified dict) This is a flexible field that can take additional JSON parameters that will be used in the JINJA templating for the SQL query or other report configuration logic. This will likely be especially important for date ranges, customer names, or other filters if you build a flexible report that can serve multiple customers.",
)

@click.option(
    "--delivery_method",
    required=True,
    default="email",
    help="This is the method that will be used to deliver the file. This can be one of the following: gcs, s3, sftp",
)

@click.option(
    "--delivery_secret_name",
    required=True,
    help="This is the name of the secret that will be used to reference buckets, connection/authentication details, email addresses that need to emailed, slack details, etc. Other authentication details (for data pull sources, etc.) are stored in the undertide config secret.",
)

@click.option(
    "--file_format",
    default=None,
    help="This is the format that the file will be delivered in.  By default, the file will be created in csv, (or delivered in the format that it is in the bucket -- so this won't apply).  This can be one of the following: csv, txt,parquet,avro",
)

@click.option(
    "--compression",
    default=None,
    help="This is the compression method that will be used to compress the file. By default None is used, unless set in the report config as a setting. This can be one of the following: gzip, zip, bz2",
)

@click.option(
    "--delivery_directory",
    required=False,
    default=None,
    help="A directory inside of the bucket that the file needs to be uploaded into.  Used in combination with delivery_method of S3",
)

@click.option(
    "--config_secret",
    required=True,
    help="undertide references a secret for its own configuration. If running via Cloud Run or Fargate, the secret should be mounted to the container at secrets/config.yml and this is not needed. If this is running in a kubernetes pod operator or ecs operator, the container will not have this config on boot, and this field should be used to specify information on how to obtain the secret that contains the config, as well as the service to use. e.g. {'secret': 'undertide-config', 'service': 'aws'} | {'secret': 'undertide-config', 'service': 'gcp', 'project': 'my-project'}",
)

@click.option(
    "--dry_run",
    required=False,
    default=False,
    help="If true, the report will not be delivered, but the file will still be exported to the archive bucket for testing purposes. The file name will indicate that it is a dry run.",
)

def build_and_send_report(
    report_name: str,
    report_config_jinja: str,
    delivery_method: str,
    delivery_secret_name: str,
    file_format: str,
    compression: str,
    delivery_directory: str,
    config_secret: str,
    dry_run: bool
    ):

    # Get the config_secret from click and determine the service to use, use it to initiate the secret manager client and secrets cache
    config_secret=json.loads(config_secret)
    secret_name = parse_callable_config(config_secret)
    # Initialize the secret manager client and secrets cache
    secrets_manager = UndertideSecretsManager()
    # Get the rest of the config from the config secret
    secret_data = secrets_manager.get_secret(secret_name)
    # Add config items as env variables
    parse_config(secret_data)

    L.info(f"Beginning building report: {report_name} for delivery to {delivery_method}")
    report = UndertideReport(
        report_name=report_name,
        report_config_jinja=json.loads(report_config_jinja),
        delivery_method=delivery_method,
        delivery_secret_name=delivery_secret_name,
        file_format=file_format,
        compression=compression,
        delivery_directory=delivery_directory,
        dry_run=dry_run
    )
    L.info(f"Report delivered as {report.delivered_report}!")

    



if __name__ == "__main__":
    build_and_send_report()
