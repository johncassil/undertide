import os
import pandas as pd
from google.cloud import bigquery
from src.logger import setup_logger

L = setup_logger()


class UndertideBigQuery:
    def __init__(self):
        self.project = os.environ.get("BIGQUERY_PROJECT")
        if self.project is None:
            self.project = os.environ.get("GCP_PROJECT")

        if self.project:
            self.client = bigquery.Client(project=self.project)
        else:
            self.client = bigquery.Client()

    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas dataframe."""
        L.info(f"Executing query: {query}")
        try:
            df = self.client.query(query).to_dataframe()

        except Exception as e:
            L.error(f"Error executing query: {e}")
            raise e

        return df
