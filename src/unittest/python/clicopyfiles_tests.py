# -*- coding: utf-8 -*-
import unittest

from awslambdahelper.cli import LambdahelperBundler
from mock import patch, call, MagicMock, mock_open


class TestBundlerFileCopy(unittest.TestCase):
    @patch('shutil.copy')
    @patch('glob.glob')
    def test_filecopy(self, glob, shutil_copy):
        glob.return_value = ('one', 'two', 'three', 'four')

        cli_tool = LambdahelperBundler()
        cli_tool.target_directory = 'target'
        cli_tool.working_directory = 'working'
        cli_tool.requirements_path = 'reqs'
        cli_tool.copy_lambda_package_files()

        shutil_copy.assert_has_calls([
            call('one', 'working'),
            call('two', 'working'),
            call('three', 'working'),
            call('four', 'working'),
            call('reqs', 'working')
        ])

        self.assertEqual(shutil_copy.call_count, 5)
