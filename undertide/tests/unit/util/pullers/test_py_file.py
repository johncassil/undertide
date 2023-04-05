import unittest
from unittest.mock import patch, MagicMock
from src.util.pullers.py_file import UndertidePyFileFinder
from datetime import datetime


def test_init_sets_variables():
    data_pull_method = "s3"
    report_name = "my_report"
    bucket = "my_bucket"
    file_format = "csv"
    dry_run = False
    user_function_str = "def find_file(client, bucket):\n  return 'my_file.csv'"

    finder = UndertidePyFileFinder(
        data_pull_method=data_pull_method,
        report_name=report_name,
        bucket=bucket,
        file_format=file_format,
        dry_run=dry_run,
        user_function_str=user_function_str,
    )

    assert finder.user_function_str == user_function_str
    assert finder.bucket_type == data_pull_method
    assert finder.bucket == bucket
    assert finder.file_format == file_format
    assert finder.report_name == report_name
    assert finder.dry_run == dry_run


class TestUndertidePyFileFinder(unittest.TestCase):
    def test_get_file_with_s3_bucket_and_csv_format(self):
        # mock S3 client
        s3_client_mock = MagicMock()
        s3_client_mock.download_file.return_value = None

        # define the function to be used by the file finder
        def find_csv_file(client, bucket):
            return "path/to/file.csv"

        # instantiate the file finder and run the test
        file_finder = UndertidePyFileFinder(
            "s3",
            "test_report",
            "test_bucket",
            "csv",
            False,
            "def find_file(client, bucket):\n    return 'path/to/file.csv'\n",
        )
        with patch("boto3.client", return_value=s3_client_mock):
            with patch.object(
                file_finder,
                "transform_file",
                return_value="path/to/transformed_file.csv",
            ) as mock_transform_file:
                file_path = file_finder.get_file()
                mock_transform_file.assert_not_called()
        self.assertEqual(
            file_path, f"test_report_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        )

    def test_get_file_with_gcs_bucket_and_parquet_format(self):
        # mock GCS client
        gcs_client_mock = MagicMock()
        bucket_mock = MagicMock()
        blob_mock = MagicMock()
        blob_mock.download_to_filename.return_value = None
        bucket_mock.blob.return_value = blob_mock
        gcs_client_mock.bucket.return_value = bucket_mock

        # define the function to be used by the file finder
        def find_parquet_file(client, bucket):
            return "path/to/file.parquet"

        # instantiate the file finder and run the test
        file_finder = UndertidePyFileFinder(
            "gcs",
            "test_report",
            "test_bucket",
            "parquet",
            False,
            "def find_file(client, bucket):\n    return 'path/to/file.parquet'\n",
        )
        with patch("google.cloud.storage.Client", return_value=gcs_client_mock):
            with patch.object(
                file_finder,
                "transform_file",
                return_value="path/to/transformed_file.parquet",
            ) as mock_transform_file:
                file_path = file_finder.get_file()
                mock_transform_file.assert_not_called()
        self.assertEqual(
            file_path,
            f"test_report_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.parquet",
        )

    def test_transform_file_with_csv_file(self):
        # define the input and expected output file names

        # define the input and expected output file formats

        # mock the pandas read_csv and to_csv functions
        pd_mock = MagicMock()
        pd_mock.read_csv.return_value = MagicMock()
        to_csv_mock = MagicMock()
        pd_mock.return_value.to_csv = to_csv_mock

        # instantiate the file finder and run the test
        UndertidePyFileFinder("s3", "test_report", "test_bucket", "csv", False, "")
        with patch("pandas.read_csv", pd_mock):
            with patch("pandas.DataFrame.to_csv", to_csv_mock):
                pass
