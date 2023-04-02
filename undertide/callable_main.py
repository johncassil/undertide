import click
import json
from src.logger import setup_logger
from src.report import UndertideReport
from src.util.secrets.secrets import SecretManager

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



# Basic workflow -- for cloud run and docker call:

# 1. Initialize the secret manager client and secrets cache
#   Docker: Get the config_secret from click and determine the service to use, use it to initiate the secret manager client and secrets cache
#   Cloud Run: Get the config_secret from mounted file secrets/config.yml and determine the service to use, use it to initiate the secret manager client and secrets cache
# 2. Get the rest of the config from the config secret
# 3. Add config items as env variables
# 4. Get the delivery secret from the delivery secret
# 5. Get the report config from the report config
# 6. Build the report
#    a. Find and execute the sql query (or other data pull method)
#    b. Write the report to a file
# 7. Compress the file if needed
# 8. Upload the file to the reports_archive_bucket 
# 9. Deliver the file to the delivery method




def build_and_send_report(
    report_name: str,
    report_config_jinja: str,
    delivery_method: str,
    delivery_secret_name: str,
    file_format: str,
    compression: str,
    delivery_directory: str,
    config_secret: str
    ):

    # config_secret=json.loads(config_secret)

    # secret_manager = SecretManager()
    # secret_value = secret_manager.get_secret('config_secret')


    L.info(f"Beginning building report: {report_name} for delivery to {delivery_method}")
    report = UndertideReport(
        report_name=report_name,
        report_config_jinja=json.loads(report_config_jinja),
        delivery_method=delivery_method,
        delivery_secret_name=delivery_secret_name,
        file_format=file_format,
        compression=compression,
        delivery_directory=delivery_directory
    )
    report

    



if __name__ == "__main__":
    build_and_send_report()
