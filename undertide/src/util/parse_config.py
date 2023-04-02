import json
import os
from src.logger import setup_logger

L = setup_logger()


def parse_config():
    """Parses the config and sets the env variables.
    The following items are expected depending on the setup:
    - cloud_provider
    - gcp_project
    - aws_region
    - aws_access_key_id
    - aws_secret_access_key
    - aws_region
    - reports_config_bucket
    - reports_archive_bucket
    - bigquery_project
    - redshift_connection_string
    - snowflake_user
    - snowflake_password
    - snowflake_account
    - snowflake_warehouse
    - snowflake_database
    - snowflake_schema
    - postgres_connection_string
    - mysql_connection_string
    - duckdb_file_bucket
    - duckdb_file_path
    """
    # Get the config_secret from mounted file secrets/config.json and determine the service to use, use it to initiate the secret manager client and secrets cache
    L.info("Getting config_secret from mounted file secrets/config.json...")
    try:
        with open("secrets/config.json", "r") as file:
            config_secret = json.load(file)
    except Exception as e:
        L.error(f"Error getting config_secret from mounted file secrets/config.json: {e}")
        raise e
    
    L.info("Getting cloud_provider and setting env variable...")
    cloud_provider = config_secret.get("cloud_provider")
    if not cloud_provider:
        L.error("cloud_provider is missing from config_secret!")
        raise Exception("cloud_provider is missing from config_secret!")
    os.environ["CLOUD_PROVIDER"] = cloud_provider

    if cloud_provider == "gcp":
        L.info("Getting gcp_project and setting env variable...")
        gcp_project = config_secret.get("gcp_project")
        if not gcp_project:
            L.error("gcp_project is missing from config_secret!")
            raise Exception("gcp_project is missing from config_secret!")
        os.environ["GCP_PROJECT"] = gcp_project
    
    elif cloud_provider == "aws":
        L.info("Getting aws_region and setting env variable...")
        aws_region = config_secret.get("aws_region")
        if not aws_region:
            L.error("aws_region is missing from config_secret!")
            raise Exception("aws_region is missing from config_secret!")
        os.environ["AWS_REGION"] = aws_region

        L.info("Getting aws_access_key_id and setting env variable...")
        aws_access_key_id = config_secret.get("aws_access_key_id")
        if not aws_access_key_id:
            L.error("aws_access_key_id is missing from config_secret!")
            raise Exception("aws_access_key_id is missing from config_secret!")
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key_id

        L.info("Getting aws_secret_access_key and setting env variable...")
        aws_secret_access_key = config_secret.get("aws_secret_access_key")
        if not aws_secret_access_key:
            L.error("aws_secret_access_key is missing from config_secret!")
            raise Exception("aws_secret_access_key is missing from config_secret!")
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key
    
    L.info("Getting reports_config_bucket and setting env variable...")
    reports_config_bucket = config_secret.get("reports_config_bucket")
    if not reports_config_bucket:
        L.error("reports_config_bucket is missing from config_secret!")
        raise Exception("reports_config_bucket is missing from config_secret!")
    os.environ["REPORTS_CONFIG_BUCKET"] = reports_config_bucket

    L.info("Getting reports_archive_bucket and setting env variable...")
    reports_archive_bucket = config_secret.get("reports_archive_bucket")
    if not reports_archive_bucket:
        L.info("reports_archive_bucket is missing from config_secret!")
        L.info("Setting reports_archive_bucket path to reports_config_bucket/delivered_reports...")
        reports_archive_bucket = f"reports_config_bucket/delivered_reports"
    os.environ["REPORTS_ARCHIVE_BUCKET"] = reports_config_bucket

    L.info("Getting bigquery_project and setting env variable...")
    bigquery_project = config_secret.get("bigquery_project")
    if not bigquery_project:
        L.info("bigquery_project is missing from config_secret!")
        L.info("Setting bigquery_project to gcp_project...")
        bigquery_project = gcp_project
    os.environ["BIGQUERY_PROJECT"] = bigquery_project

    L.info("Getting redshift_connection_string and setting env variable...")
    redshift_connection_string = config_secret.get("redshift_connection_string")
    if not redshift_connection_string:
        L.info("redshift_connection_string is missing from config_secret!")
        L.info("Setting redshift_connection_string to None...")
    os.environ["REDSHIFT_CONNECTION_STRING"] = redshift_connection_string

    L.info("Getting snowflake_user and setting env variable...")
    snowflake_user = config_secret.get("snowflake_user")
    if not snowflake_user:
        L.info("snowflake_user is missing from config_secret!")
        L.info("Setting snowflake_user to None...")
    os.environ["SNOWFLAKE_USER"] = snowflake_user

    L.info("Getting snowflake_password and setting env variable...")
    snowflake_password = config_secret.get("snowflake_password")
    if not snowflake_password:
        L.info("snowflake_password is missing from config_secret!")
        L.info("Setting snowflake_password to None...")
    os.environ["SNOWFLAKE_PASSWORD"] = snowflake_password

    L.info("Getting snowflake_account and setting env variable...")
    snowflake_account = config_secret.get("snowflake_account")
    if not snowflake_account:
        L.info("snowflake_account is missing from config_secret!")
        L.info("Setting snowflake_account to None...")
    os.environ["SNOWFLAKE_ACCOUNT"] = snowflake_account

    L.info("Getting snowflake_warehouse and setting env variable...")
    snowflake_warehouse = config_secret.get("snowflake_warehouse")
    if not snowflake_warehouse:
        L.info("snowflake_warehouse is missing from config_secret!")
        L.info("Setting snowflake_warehouse to None...")
    os.environ["SNOWFLAKE_WAREHOUSE"] = snowflake_warehouse

    L.info("Getting snowflake_database and setting env variable...")
    snowflake_database = config_secret.get("snowflake_database")
    if not snowflake_database:
        L.info("snowflake_database is missing from config_secret!")
        L.info("Setting snowflake_database to None...")
    os.environ["SNOWFLAKE_DATABASE"] = snowflake_database

    L.info("Getting snowflake_schema and setting env variable...")
    snowflake_schema = config_secret.get("snowflake_schema")
    if not snowflake_schema:
        L.info("snowflake_schema is missing from config_secret!")
        L.info("Setting snowflake_schema to None...")
    os.environ["SNOWFLAKE_SCHEMA"] = snowflake_schema

    L.info("Getting postgresql_connection_string and setting env variable...")
    postgresql_connection_string = config_secret.get("postgresql_connection_string")
    if not postgresql_connection_string:
        L.info("postgresql_connection_string is missing from config_secret!")
        L.info("Setting postgresql_connection_string to None...")
    os.environ["POSTGRESQL_CONNECTION_STRING"] = postgresql_connection_string

    L.info("Getting mysql_connection_string and setting env variable...")
    mysql_connection_string = config_secret.get("mysql_connection_string")
    if not mysql_connection_string:
        L.info("mysql_connection_string is missing from config_secret!")
        L.info("Setting mysql_connection_string to None...")
    os.environ["MYSQL_CONNECTION_STRING"] = mysql_connection_string
    
    L.info("Getting duckdb_file_bucket and setting env variable...")
    duckdb_file_bucket = config_secret.get("duckdb_file_bucket")
    if not duckdb_file_bucket:
        L.info("duckdb_file_bucket is missing from config_secret!")
        L.info("Setting duckdb_file_bucket to None...")
    os.environ["DUCKDB_FILE_BUCKET"] = duckdb_file_bucket

    L.info("Getting duckdb_file_path and setting env variable...")
    duckdb_file_path = config_secret.get("duckdb_file_path")
    if not duckdb_file_path:
        L.info("duckdb_file_path is missing from config_secret!")
        L.info("Setting duckdb_file_path to None...")
    os.environ["DUCKDB_FILE_PATH"] = duckdb_file_path
    



