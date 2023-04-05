import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.util.pullers.redshift import UndertideRedshift


class TestUndertideRedshift(unittest.TestCase):
    def setUp(self):
        self.redshift = UndertideRedshift()

    @patch('src.util.pullers.redshift.pg')
    def test_execute_query(self, mock_pg):
        # Define a sample query and result
        query = 'SELECT * FROM users'
        result = [('Alice', 25), ('Bob', 30)]
        columns = ['name', 'age']

        # Mock the redshift connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_pg.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.description = [(columns[0],), (columns[1],)]
        mock_cursor.fetchall.return_value = result

        # Execute the query and check the result
        df = self.redshift.execute_query(query)
        mock_pg.connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(query)
        self.assertEqual(columns, [desc[0] for desc in mock_cursor.description])
