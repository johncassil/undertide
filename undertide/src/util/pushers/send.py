from util.secrets.secrets import get_secret

def send_report(report, delivery_method, delivery_secret_name):
    """
    This function is used to send the report to the specified delivery method.
    The delivery method can be one of the following: sftp, s3, gcs, email, slack
    """
    delivery_secret = get_secret(delivery_secret_name)
    connection_secret = delivery_secret.get("connection_secret", "")
    upload_directory = delivery_secret.get("upload_directory", "")
    email_recipients = delivery_secret.get("email_recipients", "")
    sftp_endpoint = delivery_secret.get("sftp_endpoint", "")

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