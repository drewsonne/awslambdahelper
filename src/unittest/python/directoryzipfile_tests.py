import os
import shutil
import tempfile
import unittest
from functools import partial
from zipfile import ZipFile

from mock import patch, MagicMock, call

from awslambdahelper.cli import DirectoryZipFile


class TestArgParserTests(unittest.TestCase):
    def setUp(self):
        self.zip_structure = [
            '1',
            '2',
            '3',
            'a/1',
            'a/2',
            'a/3',
            'b/1',
            'b/2',
            'b/3'
        ]

        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('os.walk')
    def test_directoryzip_integration(self, os_walk):
        os_walk.return_value = ((self.test_dir, (), self.zip_structure),)

        mock_write = MagicMock()
        zipdirectory = DirectoryZipFile(self.test_dir)
        zipdirectory.write = mock_write
        zipdirectory.create_archive()
        zipdirectory.close()


        calls = map(lambda file: call(os.path.join(self.test_dir, file), file), self.zip_structure)
        mock_write.assert_has_calls(calls)
