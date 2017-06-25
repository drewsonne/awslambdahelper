# -*- coding: utf-8 -*-
"""
Test the CLI Argument Parser
"""
import os
import unittest
from argparse import Namespace, ArgumentError

from mock import patch, call

from awslambdahelper.cli import BundlerArgumentParser


class TestArgParserTests(unittest.TestCase):
    def setUp(self):
        self.original = dict()
        self.original['os.path.exists'] = os.path.exists
        self.original['os.path.isdir'] = os.path.exists
        self.original['os.path.expanduser'] = os.path.expanduser
        self.original['os.path.abspath'] = os.path.abspath

        self.path_exists = patch('os.path.exists').start()

        self.path_isdir = patch('os.path.isdir').start()

        self.path_expanduser = patch('os.path.expanduser').start()

        self.path_abspath = patch('os.path.abspath').start()

    def tearDown(self):
        os.path.exists = self.original['os.path.exists']
        os.path.isdir = self.original['os.path.isdir']
        os.path.expanduser = self.original['os.path.expanduser']
        os.path.abspath = self.original['os.path.abspath']

    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_not_a_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_requirements')
    def test_parser_missing_req(self, missing_requirements, not_a_directory, missing_directory):
        missing_requirements.return_value = 'missing_requirements'
        not_a_directory.return_value = None
        missing_directory.return_value = None

        parser = BundlerArgumentParser()

        with self.assertRaises(ArgumentError, parser):
            parser._parse_known_args([
                '--directory', 'world',
            ], Namespace(requirements_name='requirements.txt'))

    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_not_a_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_requirements')
    def test_parser_not_a_dir(self, missing_requirements, not_a_directory, missing_directory):
        missing_requirements.return_value = None
        not_a_directory.return_value = 'not a directory'
        missing_directory.return_value = None

        parser = BundlerArgumentParser()

        with self.assertRaises(ArgumentError, parser):
            parser._parse_known_args([
                '--directory', 'world',
            ], Namespace(requirements_name='requirements.txt'))

    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_not_a_directory')
    @patch('awslambdahelper.cli.BundlerArgumentParser._test_missing_requirements')
    @patch('awslambdahelper.cli.BundlerArgumentParser._full_path')
    def test_parser_good_response(self, full_path, missing_requirements, not_a_directory, missing_directory):
        missing_requirements.return_value = None
        not_a_directory.return_value = None
        missing_directory.return_value = None
        full_path.return_value = 'world'

        parser = BundlerArgumentParser()

        namespace, unparsed_args = parser._parse_known_args([
            '--directory', 'world',
        ], Namespace(requirements_name='requirements.txt'))

        self.assertEqual(namespace.directory, 'world')
        self.assertEqual(namespace.requirements_name, 'requirements.txt')
        self.assertEqual(namespace.requirements_path, 'world/requirements.txt')
        self.assertEqual(len(unparsed_args), 0)

    def test_missingdir_true(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = True
        missing_directory = cli_parser._test_missing_directory('my_dir')
        self.assertEqual(missing_directory, False)

    def test_missingdir_false(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = False
        missing_directory = cli_parser._test_missing_directory('my_dir')
        self.assertEqual(missing_directory, "Could not find `--directory=my_dir`.")

    def test_notdirectory_true(self):
        cli_parser = BundlerArgumentParser()

        self.path_isdir.return_value = True
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, False)

    def test_notdirectory_false(self):
        cli_parser = BundlerArgumentParser()

        self.path_isdir.return_value = False
        missing_directory = cli_parser._test_not_a_directory('my_dir')
        self.assertEqual(missing_directory, "`--directory=my_dir` is not a directory.")

    def test_missingrequirements_true(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = True
        missing_directory = cli_parser._test_missing_requirements('my_dir')
        self.assertEqual(missing_directory, False)

    def test_missingrequirements_false(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = False
        missing_directory = cli_parser._test_missing_requirements('my_dir')
        self.assertEqual(missing_directory, "Could not find requirements file at `my_dir`.")

    def test__fullpath_nohomedir(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = False
        self.path_expanduser.return_value = False
        self.path_abspath.return_value = True
        full_path = cli_parser._full_path('my_dir')

        self.path_abspath.assert_has_calls([call('my_dir')])
        self.path_expanduser.assert_not_called()

    def test__fullpath_hashomedir(self):
        cli_parser = BundlerArgumentParser()

        self.path_exists.return_value = False
        self.path_expanduser.return_value = "/home/my_dir"
        self.path_abspath.return_value = True
        full_path = cli_parser._full_path('~/my_dir')

        self.path_abspath.assert_has_calls([call('/home/my_dir')])
        self.path_exists.assert_has_calls([call('~/my_dir')])
        self.path_expanduser.assert_has_calls([call('~/my_dir')])
