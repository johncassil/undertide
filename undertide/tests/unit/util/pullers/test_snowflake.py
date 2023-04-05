import os
import pandas as pd
import snowflake.connector as snowflake
from src.logger import setup_logger

L = setup_logger()


class UndertideSnowflake:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect_to_snowflake(self):
        snowflake_user = os.environ.get("SNOWFLAKE_USER")
        snowflake_password = os.environ.get("SNOWFLAKE_PASSWORD")
        snowflake_account = os.environ.get("SNOWFLAKE_ACCOUNT")
        snowflake_warehouse = os.environ.get("SNOWFLAKE_WAREHOUSE")
        snowflake_database = os.environ.get("SNOWFLAKE_DATABASE")
        snowflake_schema = os.environ.get("SNOWFLAKE_SCHEMA")

        L.info(f"Connecting to Snowflake with user: {snowflake_user}")

        conn = snowflake.connect(
            user=snowflake_user,
            password=snowflake_password,
            account=snowflake_account,
            warehouse=snowflake_warehouse,
            database=snowflake_database,
            schema=snowflake_schema,
        )

        return conn

    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas dataframe."""
        L.info(f"Executing query: {query}")

        if self.conn is None:
            self.conn = self.connect_to_snowflake()
            self.cursor = self.conn.cursor()

        try:
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(self.cursor.fetchall(), columns=columns)
            self.cursor.close()
            self.conn.close()

        except Exception as e:
            L.error(f"Error executing query: {e}")
            raise e

        return df
