from google.cloud import bigquery
from src.logger import setup_logger
from typing import Dict

L = setup_logger()


# Explicitly turn off query cache when running EL by default
DEFAULT_QUERY_JOB_CONFIG = bigquery.QueryJobConfig(
    use_query_cache=False, priority=bigquery.QueryPriority.BATCH
)


class UndertideBigQuery:
    def __init__(
        self,
        project: str = None,
        job_config: bigquery.QueryJobConfig = DEFAULT_QUERY_JOB_CONFIG,
    ):
        if project:
            self.client = bigquery.Client(project=project)
        else:
            self.client = bigquery.Client()

    @staticmethod
    def _get_result_destination_string(
        query_destination: bigquery.job.QueryJob.destination,
    ) -> str:
        return f"{query_destination.project}:{query_destination.dataset_id}.{query_destination.table_id}"

    def execute_query(
        self,
        query: str,
        labels: Dict = None,
        job_config: bigquery.QueryJobConfig = DEFAULT_QUERY_JOB_CONFIG,
    ) -> bigquery.job.QueryJob:
        """

        Args:
            query:
            labels:
            job_config:

        Returns:

        """

        if labels:
            job_config.labels = labels

        query_job = self.client.query(query, job_config=job_config)
        query_job.result()

        return query_job

    def export_to_gcs(
        self,
        job: bigquery.job.QueryJob,
        gcs_bucket: str,
        file_name: str,
        use_compression: bool = True,
    ) -> bigquery.ExtractJob:
        gcs_destination_uri = f"gs://{gcs_bucket}/{file_name}"

        extract_job = self.client.extract_table(
            job.destination,
            gcs_destination_uri,
            job_config=bigquery.ExtractJobConfig(
                compression="GZIP" if use_compression else "None"
            ),
        )

        extract_job.result()

        return extract_job
