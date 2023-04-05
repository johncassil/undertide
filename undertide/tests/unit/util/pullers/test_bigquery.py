import os
from google.cloud import bigquery
from unittest.mock import MagicMock, patch
from src.util.pullers.bigquery import UndertideBigQuery


class TestUndertideBigQuery:
    def setup_method(self):
        self.client_mock = MagicMock(spec=bigquery.Client)
        self.query = "SELECT * FROM mytable"

    def test_execute_query_with_project(self):
        os.environ["BIGQUERY_PROJECT"] = "myproject"
        with patch.object(bigquery, "Client", return_value=self.client_mock):
            bq = UndertideBigQuery()
            df = bq.execute_query(self.query)
            self.client_mock.query.assert_called_once()
            print(self.client_mock.query.call_args)
            assert self.client_mock.query.call_args[0][0] == self.query
            assert df.empty

    def test_execute_query_without_project(self):
        with patch.object(bigquery, "Client", return_value=self.client_mock):
            bq = UndertideBigQuery()
            df = bq.execute_query(self.query)
            self.client_mock.query.assert_called_once()
            print(self.client_mock.query.call_args)
            assert self.client_mock.query.call_args[0][0] == self.query
            assert df.empty
