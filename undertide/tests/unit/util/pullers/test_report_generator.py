import pytest
import unittest
from unittest.mock import patch
from src.util.pullers.report_generator import UndertideSqlReportGenerator


def test_execute_query_invalid_db_type():
    report_gen = UndertideSqlReportGenerator("invalid_db_type")

    with pytest.raises(ValueError):
        report_gen.execute_query("SELECT * FROM my_table")


class TestUndertideSqlReportGenerator(unittest.TestCase):
    @patch("src.util.pullers.report_generator.UndertideBigQuery")
    def test_get_client_bigquery(self, mock_bigquery):
        generator = UndertideSqlReportGenerator("bigquery")
        client = generator._get_client()
        mock_bigquery.assert_called_once()
        self.assertEqual(client, mock_bigquery.return_value)

    @patch("src.util.pullers.report_generator.UndertideSnowflake")
    def test_get_client_snowflake(self, mock_snowflake):
        generator = UndertideSqlReportGenerator("snowflake")
        client = generator._get_client()
        mock_snowflake.assert_called_once()
        self.assertEqual(client, mock_snowflake.return_value)

    @patch("src.util.pullers.report_generator.UndertideRedshift")
    def test_get_client_redshift(self, mock_redshift):
        generator = UndertideSqlReportGenerator("redshift")
        client = generator._get_client()
        mock_redshift.assert_called_once()
        self.assertEqual(client, mock_redshift.return_value)

    @patch("src.util.pullers.report_generator.UndertidePostgres")
    def test_get_client_postgres(self, mock_postgres):
        generator = UndertideSqlReportGenerator("postgres")
        client = generator._get_client()
        mock_postgres.assert_called_once()
        self.assertEqual(client, mock_postgres.return_value)

    @patch("src.util.pullers.report_generator.UndertideMysql")
    def test_get_client_mysql(self, mock_mysql):
        generator = UndertideSqlReportGenerator("mysql")
        client = generator._get_client()
        mock_mysql.assert_called_once()
        self.assertEqual(client, mock_mysql.return_value)

    @patch("src.util.pullers.report_generator.UndertideDuckDB")
    def test_get_client_duckdb(self, mock_duckdb):
        generator = UndertideSqlReportGenerator("duckdb")
        client = generator._get_client()
        mock_duckdb.assert_called_once()
        self.assertEqual(client, mock_duckdb.return_value)

    def test_get_client_invalid_type(self):
        generator = UndertideSqlReportGenerator("invalid_type")
        with self.assertRaises(ValueError):
            generator._get_client()
