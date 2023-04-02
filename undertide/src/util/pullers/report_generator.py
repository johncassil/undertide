import pandas as pd
from src.util.pullers.bigquery import UndertideBigQuery
from src.util.pullers.snowlake import UndertideSnowflake
from src.util.pullers.redshift import UndertideRedshift
from src.util.pullers.postgres import UndertidePostgres
from src.util.pullers.mysql import UndertideMysql
from src.util.pullers.duckdb import UndertideDuckDB


class UndertideSqlReportGenerator():
    def __init__(self, db_type: str:
        self.db_type = db_type

    def execute_query(self, query: str) -> pd.DataFrame:
        if self.db_type == 'bigquery':
            client = UndertideBigQuery()
            return client.execute_query(query)
        
        elif self.db_type == 'snowflake':
            client = UndertideSnowflake()
            return client.execute_query(query)
    
        elif self.db_type == 'redshift':
            client = UndertideRedshift()
            return client.execute_query(query)

        elif self.db_type == 'postgres':
            client = UndertidePostgres()
            return client.execute_query(query)

        elif self.db_type == 'mysql':
            client = UndertideMysql()
            return client.execute_query(query)

        elif self.db_type == 'duckdb':
            client = UndertideDuckDB()
            return client.execute_query(query)

        else:
            raise ValueError('Invalid database type')
