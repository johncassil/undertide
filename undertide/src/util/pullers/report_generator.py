import pandas as pd
from src.util.pullers.bigquery import UndertideBigQuery
from src.util.pullers.snowlake import UndertideSnowflake
from src.util.pullers.redshift import UndertideRedshift
from src.util.pullers.postgres import UndertidePostgres
from src.util.pullers.mysql import UndertideMysql
from src.util.pullers.duckdb import UndertideDuckDB


class UndertideSqlReportGenerator:
    def __init__(self, db_type: str):
        self.db_type = db_type
        self.client = None

    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas dataframe."""
        self.client = self._get_client()
        return self.client.execute_query(query)

    def _get_client(self):
        if self.db_type == "bigquery":
            return UndertideBigQuery()
        elif self.db_type == "snowflake":
            return UndertideSnowflake()
        elif self.db_type == "redshift":
            return UndertideRedshift()
        elif self.db_type == "postgres":
            return UndertidePostgres()
        elif self.db_type == "mysql":
            return UndertideMysql()
        elif self.db_type == "duckdb":
            return UndertideDuckDB()
        else:
            raise ValueError(f"Invalid db_type: {self.db_type}")
