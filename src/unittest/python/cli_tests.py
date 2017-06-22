import unittest

from mock import patch

from awslambdahelper.cli import BundlerArgumentParser


class TestArgParserTests(unittest.TestCase):
    @patch('os.path.exists')
    def test_missingdir_true(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = True
        missing_directory = cli_parser._test_missing_directory('my_dir')
        self.assertEqual(missing_directory, False)

    @patch('os.path.exists')
    def test_missingdir_false(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = False
        missing_directory = cli_parser._test_missing_directory('my_dir')
        self.assertEqual(missing_directory, "Could not find `--directory=my_dir`.")

    @patch('os.path.isdir')
    def test_notdirectory_true(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = True
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, False)

    @patch('os.path.isdir')
    def test_notdirectory_false(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = False
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, "`--directory=my_dir` is not a directory.")
