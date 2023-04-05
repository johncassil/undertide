import os
import pandas as pd
import duckdb
from src.logger import setup_logger

L = setup_logger()


class UndertideDuckDB:
    def __init__(self):
        self.file_name = self.connect_to_duckdb()

    def connect_to_duckdb():
        duckdb_file = os.environ.get("DUCKDB_FILE_PATH")
        duck_db_file_bucket = os.environ.get("DUCKDB_FILE_BUCKET")
        L.info(
            f"Connecting to DuckDB! Using file: {duckdb_file} "
            f"in bucket: {duck_db_file_bucket}"
        )
        ## TODO: Implement cloud agnostic pull of file locally.
        ## TODO: Write tests for this.

        # return file_path

    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas dataframe."""
        L.info(f"Executing query: {query}")

        try:
            duckdb.sql(query).df()

        except Exception as e:
            L.error(f"Error executing query: {e}")
            raise e

        # return df
