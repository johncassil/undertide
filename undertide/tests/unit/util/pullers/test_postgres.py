import unittest
import os
from unittest.mock import patch, MagicMock
from src.util.pullers.postgres import UndertidePostgres


class TestUndertidePostgres(unittest.TestCase):
    def setUp(self):
        self.postgres = UndertidePostgres()

    @patch("src.util.pullers.postgres.pg.connect")
    def test_execute_query(self, mock_connect):
        # Define a sample query and result
        query = "SELECT * FROM users"
        result = [("Alice", 25), ("Bob", 30)]
        columns = ["name", "age"]

        # Mock the postgres connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [(columns[0],), (columns[1],)]
        mock_cursor.fetchall.return_value = result

        # Execute the query and check the result
        self.postgres.execute_query(query)
        mock_connect.assert_called_once_with(
            os.environ.get("POSTGRES_CONNECTION_STRING")
        )
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(query)
        self.assertEqual(columns, [desc[0] for desc in mock_cursor.description])
