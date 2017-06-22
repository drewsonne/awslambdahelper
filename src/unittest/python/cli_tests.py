import unittest

from mock import patch, call

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
    def test_notdirectory_true(self, path_isdir):
        cli_parser = BundlerArgumentParser()

        path_isdir.return_value = True
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, False)

    @patch('os.path.isdir')
    def test_notdirectory_false(self, path_isdir):
        cli_parser = BundlerArgumentParser()

        path_isdir.return_value = False
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, "`--directory=my_dir` is not a directory.")

    @patch('os.path.exists')
    def test_missingrequirements_true(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = True
        missing_directory = cli_parser._test_missing_requirements('my_dir')
        self.assertEqual(missing_directory, False)

    @patch('os.path.exists')
    def test_missingrequirements_false(self, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = False
        missing_directory = cli_parser._test_missing_requirements('my_dir')
        self.assertEqual(missing_directory, "Could not find requirements file at `my_dir`.")

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    @patch('os.path.abspath')
    def test__fullpath_nohomedir(self, abspath, expanduser, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = False
        expanduser.return_value = False
        abspath.return_value = True
        full_path = cli_parser._full_path('my_dir')

        abspath.assert_has_calls([call('my_dir')])
        path_exists.assert_not_called()
        expanduser.assert_not_called()

    @patch('os.path.exists')
    @patch('os.path.expanduser')
    @patch('os.path.abspath')
    def test__fullpath_hashomedir(self, abspath, expanduser, path_exists):
        cli_parser = BundlerArgumentParser()

        path_exists.return_value = False
        expanduser.return_value = "/home/my_dir"
        abspath.return_value = True
        full_path = cli_parser._full_path('~/my_dir')

        abspath.assert_has_calls([call('/home/my_dir')])
        path_exists.assert_has_calls([call('~/my_dir')])
        expanduser.assert_has_calls([call('~/my_dir')])
