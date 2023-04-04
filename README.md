<p align="center">
  <img src="etc/undertide.png" alt="undertide logo" width="450"/>
</p>

## undertide

[![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)
![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/johncassil/undertide) 
![Lifecycle:
maturing](https://img.shields.io/badge/lifecycle-experimental-blueviolet.svg)
[![CI Badge](https://github.com/johncassil/undertide/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/johncassil/undertide/actions/workflows/main.yml)


undertide is an open source data pipeline tool that allows you to run SQL queries and deliver the results to a variety of destinations in a variety of formats. It is built as an http callable that can be used easily with [Apache Airflow](https://airflow.apache.org/) and is designed to be used as a part of the modern data stack along with tools like [dbt](https://www.getdbt.com/).


## Why undertide?
Most explanations and diagrams of the modern data stack look like this:

![modern data stack](/etc/modern_data_stack.png)

They include data going into the warehouse, being transformed, and then being used in BI tools. Some have an additional section for Reverse ETL and include vendors like hightouch that can pull data from your warehouse and deliver it to places like Salesforce.  However, there is a clear gap in the data stack for delivering data from your warehouse to your own customers and partners through scheduled pulls.  This is rather boring work that inevitably every data company needs to do, and many companies have handrolled python scripts or dags to do this very common use case.  As time goes on, the configuration for these scripts and dags becomes more and more complex, and it becomes harder and harder to maintain. 

This is where undertide comes in.  It allows you to run simple SQL queries to pull from your curated datasets and deliver the results via a file sent somewhere.  Need to send a gzipped csv to a partner every day at 5am UTC?  Need to generate a parquet file and send it to a customer's GCS bucket?  Need to send a txt file to an SFTP server?  Undertide can do all of these things and more.


<br />
<br />

## undertide is currently significantly under development.

It is not yet ready for production use.  Heavy development is currently underway, and the API is subject to change.  Many adapters are currently being built and tested.
<br />
<br />



## Infrastructure/backend options 

undertide is a standalone docker image that can be deployed to a variety of cloud providers. The API can then be called from schedulers like Airflow & Dagster to serve up and send out reports.  The app is stateless and can be scaled horizontally to meet demand, deployed in a serverless fashion, meaning that you only pay for the time that the app is running.  Alternatively, you can deploy the container and call it from airflow using a kubernetes pod operator or ecs operator.

undertide was designed for airflow, so it can be configured to use the same bucket that airflow uses, meaning that you can store your sql queries in the same place as your dags. This makes it easy to manage and deploy with version-control and CI/CD.  However, if you don't use airflow, you can still use undertide by storing your sql queries in a bucket of your choice.

undertide currently supports:
- GCP (using Cloud Run, GCS, GCP Secret Manager)

undertide will soon support:
- AWS (using Fargate, S3, and AWS Secrets manager)

## Data pull options
undertide supports multiple options to pull data that is used to send out.  These can be mix and matched depending on your infrastructure. For example, you can use BigQuery to execute a query for one report, and postgres or snowflake for another report.  Additionally, if the file has already been produced by some process and is currently sitting in a bucket, undertide can pull that file and send it out.

undertide currently supports:
- BigQuery
- Snowflake
- Redshift
- Postgres
- MySQL
- S3 file pulls
- GCS file pulls

undertide will soon support:
- DuckDB

## File Format options
undertide supports the following options:
- CSV
- TXT
- Parquet
- avro
- anything else if it's already in a bucket

## Delivery options
undertide supports delivering to the following options:
- GCS bucket
- S3 bucket
- SFTP server

undertide will soon support:
- Email
- Slack

## Arguments
When undertide is called, it takes a json object as an argument.  The json object can contain the following fields for maximum flexibility:
- report_name (string)
    - The configuration for reports are stored in a bucket that you specify, and this is the name/path of the yaml file that contains the configuration for the report, for example, what data pull method to use, which sql file to use, or what logic to use to pull the file from a bucket (e.g. glob pattern, file name, etc).  In the future, this may also include emailing template or slack message template.

- report_config (stringified dict)
    - This is a flexible field that can take additional JSON parameters that will be used in the JINJA templating for the SQL query or other report configuration logic.  This will likely be especially important for date ranges, customer names, or other filters if you build a flexible report that can serve multiple customers.

- delivery_method (string)
    - This is the method that will be used to deliver the file.  This can be one of the following:
        - gcs
        - s3
        - sftp
        - email
        - slack

- delivery_secret_name (string)
    - This is the name of the secret that will be used to reference bucket, connection/authentication details, email addresses that need to emailed, slack details, etc. Other authentication details (for data pull sources, etc.) are stored in the undertide config secret.

- file_format (string) (optional)
    - This is the format that the file will be delivered in.  By default, the file will be created in csv, (or delivered in the format that it is in the bucket -- so this won't apply).  This can be one of the following:
        - csv
        - txt
        - parquet
        - avro

- compression (string) (optional)
    - This is the compression method that will be used to compress the file.  By default 'none' is used, unless set in the report config as a setting. This can be one of the following:
        - none
        - gzip
        - zip
        - bz2

- delivery_directory (string) (optional)
    - This is the directory that the file will be delivered to.  By default, the file will be delivered to the root directory.  This is useful if you want to deliver the file to a specific directory in the bucket, or if you want to deliver the file to a specific directory on the SFTP server.

- config_secret (stringified dict) (conditionally optional)
    - undertide references a secret for its own configuration.  If running via Cloud Run or Fargate, the secret should be mounted to the container at secrets/config.json and this is not needed.  If this is running in a kubernetes pod operator or ecs operator, the container will not have this config on boot, and this field should be used to specify information on how to obtain the secret that contains the config, as well as the service to use. ( e.g. '{"cloud_provider" : "aws", "aws_region" : "my-region", "secret_name": "undertide-config"}' | '{"cloud_provider": "gcp", "gcp_project": "my-project", "secret_name": "undertide-config"}' )
    Because AWS may need additonal credentials to access the secret, the docker image can also be run by passing in the following environment variables (This should not be needed in GCP, as the service account that is running the container should have access to the secret):
        - AWS_ACCESS_KEY_ID (string)
        - AWS_SECRET_ACCESS_KEY (string)
    

## Configuration secret
The configuration secret is a json file that expects the following fields depending on the infrastructure that you are using:
- cloud_provider (string) - This is the cloud provider that undertide is running on.  This can be one of the following:
    - gcp
    - aws
- gcp_project (string) - This is the GCP project that undertide is running on.  This is only needed if the cloud_provider is set to gcp. This is used to reference the GCP secret manager.
- aws_region (string) - This is the AWS region that undertide is running on.  This is only needed if the cloud_provider is set to aws. This is used to reference the AWS secrets manager.
- aws_access_key_id (string) - This is the AWS access key that undertide is running on.  This is only needed if the cloud_provider is set to aws. This is used to reference the AWS secrets manager.
- aws_secret_access_key (string) - This is the AWS secret access key that undertide is running on.  This is only needed if the cloud_provider is set to aws. This is used to reference the AWS secrets manager.
- reports_config_bucket (string) - This is the bucket that contains the report configuration files.  This is where your shared repo will sync data to, and where undertide will look for the report configuration files.
- reports_archive_bucket (string) - This is the bucket that contains a copy of all of the files that have been delivered by undertide.  This is useful for debugging and auditing purposes, and can be used to generate reports on what has been delivered to customers.  A policy can be set on the bucket to retain files for a certain amount of time, or indefinitely. If not set, this will default to the same bucket that reports are configured in, in a directory called 'delivered_reports'.
- bigquery_project (string) - This is the GCP project that contains the bigquery data that will be pulled.  This is only needed if a data_pull_method is set to bigquery. This is used to reference the GCP secret manager.
- redshift_connection_string (string) - This is the connection string that will be used to connect to redshift.  This is only needed if a data_pull_method is set to redshift.
- snowflake_user (string) - This is the snowflake user that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- snowflake_password (string) - This is the snowflake password that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- snowflake_account (string) - This is the snowflake account that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- snowflake_warehouse (string) - This is the snowflake warehouse that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- snowflake_database (string) - This is the snowflake database that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- snowflake_schema (string) - This is the snowflake schema that will be used to connect to snowflake.  This is only needed if a data_pull_method is set to snowflake.
- postgres_connection_string (string) - This is the connection string that will be used to connect to postgres.  This is only needed if a data_pull_method is set to postgres.
- mysql_connection_string (string) - This is the connection string that will be used to connect to mysql.  This is only needed if a data_pull_method is set to mysql.
- duckdb_file_bucket (string) - This is the bucket that contains the duckdb file that will be used to pull data.  This is only needed if a data_pull_method is set to duckdb.
- duckdb_file_path (string) - This is the path to the duckdb file that will be used to pull data.  This is only needed if a data_pull_method is set to duckdb.

## Report configuration
The report configuration is a yaml file that expects the following fields:
- data_pull_method (string) - This is the method that will be used to pull the data.  This can be one of the following:
    - s3
    - gcs
    - bigquery
    - snowflake
    - redshift
    - postgres
    - mysql
    - duckdb
- file_format (string) - This is the format that the file will be delivered in.  This can be one of the following, or defaults to csv:
    - csv
    - txt
    - parquet
    - avro
- compression (string) - This is the compression method that will be used to compress the file.  This can be one of the following:
    - none
    - gzip
    - zip
    - bz2
- sql_file (string) - This is the name of the sql file that will be used to pull the data.  This file should be stored in the same bucket as the report configuration file.  By convention, this file should be stored in a directory 'reports/sql'.
- python_file (string) - If you are using s3 or gcs as your data_pull_method, you can also specify a file selection function.  This is useful if you want to pull data from a specific file in a bucket, or if you want to pull data from a specific file in a directory in a bucket. This is the name of the python file that will be used to pull the data if it's not a sql-based backend.  This file should be stored in the same bucket as the report configuration file. By convention, this file should be stored in a directory 'reports/python'.  The file should contain a function definition for def find_file(bucket). Here are a couple of examples:

```python
def find_file(bucket):
    for obj in bucket.objects.all():
        if obj.key.endswith('.csv') and obj.last_modified >= datetime(2023, 3, 1):
            return obj.key
    return None 
```

```python

import datetime

def find_file(bucket):
    # Define the directory to search in
    directory = 'reports/'

    # Define the prefix to filter for CSV files
    prefix = directory + '*.csv'

    # Get a list of objects matching the prefix
    objects = list(bucket.objects.filter(Prefix=prefix))

    # Filter for objects with a timestamp in the last 2 days
    objects = [obj for obj in objects if obj.last_modified >= datetime.datetime.now() - datetime.timedelta(days=2)]

    # Sort the objects by last modified time
    objects.sort(key=lambda obj: obj.last_modified, reverse=True)

    # Return the key of the most recent object, or None if no objects found
    return objects[0].key if objects else None
```


## Delivery Secret
The delivery secret is a secret in JSON format that expects the following fields depending on the delivery method that you are using:
- gcs
    - bucket (string) - This is the bucket that the file will be delivered to.
    - credentials (string) - This is the key to the service account that will be used to authenticate to GCS.  This is only needed if the cloud_provider is set to gcp. This is used to reference the GCP secret manager.
- s3
    - bucket (string) - This is the bucket that the file will be delivered to.
    - aws_access_key_id (string) - This is the access key that will be used to authenticate to S3.
    - aws_secret_access_key (string) - This is the secret key that will be used to authenticate to S3.
- sftp
    - host (string) - This is the host/endpoint that the file will be delivered to.
    - port (string) - This is the port that the file will be delivered to. (Optional, defaults to 22)
    - username (string) - This is the username that will be used to authenticate to SFTP.
    - password (string) - This is the password that will be used to authenticate to SFTP.
- delivery_directory (string) (optional)
    - This is the directory that the file will be delivered to.  By default, the file will be delivered to the root directory.  This is useful if you want to deliver the file to a specific directory in the bucket, or if you want to deliver the file to a specific directory on the SFTP server. Can also be set/overridden in the call to undertide if a customer has different reports going to different directories.


## Installation
This is currently a work in progress.  At the moment, you can build the docker image locally or pull from the github hosted image. Terraform templates will also be provided for deploying to GCP and AWS.

## Coming soon
- --dry-run flag to query the data source and put the resulting file in the archive bucket (with 'dry-run' in the filename to be clear that it did not get sent) -- helpful for testing.
- Support for more data sources & testing
- File type transformations for files existing in buckets (parquet -> csv, etc)
- Testing Full support for the airflow workflow (Need to replace CMD with `python undertide/callable_main.py`)
- Examples of how to use undertide
- A repo to get started with CI/CD for undertide (report config files, terraform templates, an airflow dag with flexible config to call undertide, etc.)
- Full support for shipping files (instead of SQL-based reports)
- Support for more delivery methods (email, slack, etc.)
