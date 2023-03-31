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

undertide is a standalone docker image that can be deployed to a variety of cloud providers. The API can then be called from schedulers like Airflow & Dagster to serve up and send out reports.  The app is stateless and can be scaled horizontally to meet demand, deployed in a serverless fashion, meaning that you only pay for the time that the app is running.  

undertide was designed for airflow, so it can be configured to use the same bucket that airflow uses, meaning that you can store your sql queries in the same place as your dags. This makes it easy to manage and deploy with version-control and CI/CD.  However, if you don't use airflow, you can still use undertide by storing your sql queries in a bucket of your choice.

undertide currently supports:
- GCP (using Cloud Run, GCS, GCP Secret Manager)

undertide will soon support:
- AWS (using Fargate, S3, and AWS Secrets manager)

# Database options
undertide supports the following options:
- BigQuery

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

# Delivery options
undertide supports the following options:
- GCS
- S3
- SFTP

undertide will soon support:
- Email
- Slack

## Installation
This is currently a work in progress.  At the moment, you can build the docker image locally and run it.  In the future, we will have a docker image hosted.  Terraform templates will also be provided for deploying to GCP and AWS.

# Arguments
- Report (Are sql queries stored in a bucket?)
- Additional JSON parameters for SQL query (including date)
- Delivery method (s3, gcs, sftp, email, slack, etc)
- Secret name for reference for connection details, email details, slack details, etc
- Compression (gzip, zip, bz2, default = false)
- Delivery Directory for s3, gcs, sftp
