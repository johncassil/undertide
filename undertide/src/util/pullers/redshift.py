import os
import pandas as pd
import psycopg2 as pg
from src.logger import setup_logger

L = setup_logger()


class UndertideRedshift:
    def __init__(self):
        self.conn = self.connect_to_redshift()
        self.cursor = self.conn.cursor()

    def connect_to_redshift():
        L.info(f"Connecting to Redshift!")
        connection_string = os.environ.get('REDSHIFT_CONNECTION_STRING')
        conn = pg.connect(connection_string)
        return conn

    def execute_query(
        self,
        query: str
    ) -> pd.DataFrame:
        """Executes a query and returns the results as a pandas dataframe.
        """                
        L.info(f"Executing query: {query}")
        
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
