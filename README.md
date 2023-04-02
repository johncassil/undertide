# !! currently significantly under development.  This is not ready for production use yet.

<p align="center">
  <img src="etc/undertide.png" alt="undertide logo" width="750"/>
</p>

## undertide

[![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)
![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/silverton-io/buz) 
[![CI Badge](https://github.com/johncassil/undertide/actions/workflows/main.yml/badge.svg?event=push)](https://github.com/johncassil/undertide/actions/workflows/main.yml)


is an open source data pipeline tool that allows you to run SQL queries and deliver the results to a variety of destinations in a variety of formats. It is built as an http callable that can be used easily with [Apache Airflow](https://airflow.apache.org/) and is designed to be used as a part of the modern data stack along with tools like [dbt](https://www.getdbt.com/).

Most explanations and diagrames of the modern data stack include data going into the warehouse, being transformed, and then being used in BI tools. Some have an additional section for Reverse ETL and include vendors like hightouch that can pull data from your warehouse and deliver it to places like Salesforce.  However, there is a clear gap in the data stack for delivering data from your warehouse to your own customers and partners through scheduled pulls.  This is something that inevitably every data company needs to do, and mMny companies have handrolled python scripts or dags to do this very common use case.

This is where undertide comes in.  It allows you to run simple SQL queries to pull from your curated datasets and deliver the results via a file sent somewhere.  Need to send a gzipped csv to a partner every day at 5am UTC?  Need to generate a parquet file and send it to a customer's GCS bucket?  Need to send a txt file to an SFTP server?  Undertide can do all of these things and more.


# Infrastructure/backend options 

undertide is a standalone docker image that can be deployed to a variety of cloud providers. The API can then be called from schedulers like Airflow & Dagster to serve up and send out reports.  The app is stateless and can be scaled horizontally to meet demand, deployed in a serverless fashion, meaning that you only pay for the time that the app is running.  Alternatively, you can deploy the container and call it from airflow using a kubernetes pod operator or ecs operator.

undertide was designed for airflow, so it can be configured to use the same bucket that airflow uses, meaning that you can store your sql queries in the same place as your dags. This makes it easy to manage and deploy with version-control and CI/CD.  However, if you don't use airflow, you can still use undertide by storing your sql queries in a bucket of your choice.

undertide currently supports:
- GCP (using Cloud Run, GCS, GCP Secret Manager)

undertide will soon support:
- AWS (using Fargate, S3, and AWS Secrets manager)

# Data pull options
undertide supports multiple options to pull data that is used to send out.  These can be mix and matched depending on your infrastructure. For example, you can use BigQuery to execute a query for one report, and postgres or snowflake for another report.  Additionally, if the file has already been produced by some process and is currently sitting in a bucket, undertide can pull that file and send it out.

undertide currently supports:
- BigQuery 
- S3 file pulls
- GCS file pulls

undertide will soon support:
- Snowflake
- Redshift
- PostgreSQL
- DuckDB

# File Format options
undertide supports the following options:
- CSV
- TXT
- Parquet
- avro
- anything else if it's already in a bucket

# Delivery options
undertide supports the following options:
- GCS
- S3
- SFTP

undertide will soon support:
- Email
- Slack

# Arguments
When undertide is called, it takes a json object as an argument.  The json object can contain the following fields for maximum flexibility:
- report_name (string)
    - The configuration for reports are stored in a bucket that you specify, and this is the name/path of the yaml file that contains the configuration for the report, for example, what data pull method to use, which sql file to use, or what logic to use to pull the file from a bucket (e.g. glob pattern, file name, etc).  In the future, this may also include emailing template or slack message template.

- report_config (dict)
    - This is a flexible field that can take additional JSON parameters that will be used in the JINJA templating for the SQL query or other report configuration logic.  This will likely be especially important for date ranges, customer names, or other filters if you build a flexible report that can serve multiple customers.

- delivery_method (string)
    - This is the method that will be used to deliver the file.  This can be one of the following:
        - gcs
        - s3
        - sftp
        - email
        - slack

- delivery_secret_name (string)
    - This is the name of the secret that will be used to reference connection/authentication details, email addresses that need to emailed, slack details, etc. Other authentication details (for data pull sources, etc.) are stored in the undertide config secret.

- compression (string) (optional)
    - This is the compression method that will be used to compress the file.  By default 'none' is used, unless set in the report config as a setting. This can be one of the following:
        - none
        - gzip
        - zip
        - bz2

- delivery_directory (string) (optional)
    - This is the directory that the file will be delivered to.  By default, the file will be delivered to the root directory.  This is useful if you want to deliver the file to a specific directory in the bucket, or if you want to deliver the file to a specific directory on the SFTP server.

- config_secret_name (dict) (conditionally optional)
    - undertide references a secret for its own configuration.  If running via Cloud Run or Fargate, the secret should be mounted to the container at secrets/config.yml and this is not needed.  If this is running in a kubernetes pod operator or ecs operator, the container will not have this config on boot, and this field should be used to specify the name of the secret that contains the config, as well as the service to use. e.g. {"secret": "undertide-config", "service": "aws"}

## Installation
This is currently a work in progress.  At the moment, you can build the docker image locally and run it.  In the future, we will have a docker image hosted.  Terraform templates will also be provided for deploying to GCP and AWS.

