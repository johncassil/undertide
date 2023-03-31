import click
import json
from datetime import datetime
from src.logger import setup_logger
from src.reports.customer_report.customer_report import CustomerReport
from src.util.sftp import UndertideSftp
from src.util.s3 import UndertideS3

L = setup_logger()


@click.command()
@click.option(
    "--site", required=True, help="The site name to run the customer report for."
)
@click.option(
    "--report_name",
    required=True,
    help="The name of the report to produce (matches sql file name).",
)
@click.option(
    "--use_compression",
    default="true",
    help="Final report will be compressed if set to 'True'.",
)
@click.option(
    "--delivery_method",
    required=False,
    default="email",
    help="Specifies whether delivery method to be used is 'email', upload to 'sftp' endpoint, or upload to S3 bucket.",
)
@click.option(
    "--email_recipients",
    required=False,
    default="",
    help="List of email addresses to send the report to.",
)
@click.option(
    "--connection_secret",
    required=False,
    default="",
    help="Reference to the bucket and a secret name which has relevant credentials to send the report to.",
)
@click.option(
    "--upload_directory",
    required=False,
    default=None,
    help="A directory inside of the bucket that the file needs to be uploaded into.  Used in combination with delivery_method of S3",
)
@click.option(
    "--sftp_endpoint",
    required=False,
    help="Stringified dictionary with sftp endpoint host, port, and credentials secret name. "
    "Optional home directory can be included.",
)
@click.option(
    "--report_bucket",
    required=True,
    help="GCS bucket where copy of report will be uploaded to.",
)
@click.option(
    "--kms_key_project_id",
    required=True,
    help="Project ID for project with KMS resources.",
)
@click.option(
    "--big_query_project_id",
    required=False,
    default=None,
    help="Project ID for project with Big Query resources.",
)
@click.option(
    "--cloud_sql_project",
    required=False,
    default="",
    help="Optional parameter if used in sql.",
)
@click.option(
    "--days_back",
    required=False,
    default="1",
    help="Number of look back days for generating report.",
)
@click.option(
    "--execution_date",
    required=False,
    default=None,
    help="Report execution date (corresponds to report end_datetime).",
)
@click.option(
    "--report_columns",
    required=False,
    default=None,
    help="Comma separated stringified list of column names to include in the output report. The base sql used to "
    "generate the report must output these columns otherwise a sql error will occur. Do not include spaces "
    "before/after commas.",
)
def generate_customer_report(
    site: str,
    report_name: str,
    use_compression: str,
    delivery_method: str,
    email_recipients: str,
    sftp_endpoint: str,
    report_bucket: str,
    cloud_sql_project: str,
    kms_key_project_id: str,
    big_query_project_id: str,
    days_back: str,
    execution_date: str,
    report_columns: str,
    connection_secret: str,
    upload_directory: str,
) -> None:
    L.info("Beginning creation of customer report {} for {}".format(report_name, site))

    if execution_date:
        execution_date = datetime.strptime(execution_date, "%Y-%m-%dT%H:%M:%S%z").date()

    if report_columns:
        report_columns = report_columns.split(",")

    customer_report_obj = CustomerReport(
        report_name=report_name,
        site_name=site,
        report_gcs_bucket=report_bucket,
        kms_key_project_id=kms_key_project_id,
        big_query_project_id=big_query_project_id,
        cloud_sql_project=cloud_sql_project,
        days_back=int(days_back),
        execution_date=execution_date,
        report_column_filter=report_columns,
    )

    report = customer_report_obj.generate_report()
    file_name = customer_report_obj.upload_report(
        job=report, use_compression=True if use_compression.lower() == "true" else False
    )

    if delivery_method.lower() == "email":
        if len(email_recipients) == 0:
            raise ValueError(
                "List of email recipients must be provided for delivery method of email."
            )

        email_recipients = email_recipients.replace(" ", "").split(",")
        customer_report_obj.email_report(
            file_name=file_name, to_emails=email_recipients
        )
    elif delivery_method.lower() == "sftp":
        if len(sftp_endpoint) == 0:
            raise ValueError(
                "SFTP endpoint must be provided for delivery method of sftp."
            )

        sftp_config = json.loads(sftp_endpoint)
        sftp_obj = UndertideSftp(
            host=sftp_config.get("host", None),
            port=sftp_config.get("port", None),
            creds_secret=sftp_config.get("auth_secret", ""),
        )

        customer_report_obj.load_report_to_sftp(
            src_file_name=file_name,
            sftp_obj=sftp_obj,
            sftp_directory=sftp_config.get("directory", None),
        )
    elif delivery_method.lower() == "s3":
        if len(connection_secret) == 0:
            raise ValueError(
                "A connection secret should be specified for delivery method of s3."
            )

        s3_obj = UndertideS3(creds_secret=connection_secret)
        customer_report_obj.load_report_to_s3(
            src_file_name=file_name, s3_obj=s3_obj, s3_directory=upload_directory
        )
    else:
        raise ValueError(
            f"Specified delivery method, {delivery_method}, is not supported."
        )


if __name__ == "__main__":
    generate_customer_report()
