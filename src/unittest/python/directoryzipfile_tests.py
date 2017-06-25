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
        self.zip_directory = os.path.join(self.test_dir, 'zip_dir')
        os.makedirs(self.zip_directory)
        os.makedirs(os.path.join(self.zip_directory, 'a'))
        os.makedirs(os.path.join(self.zip_directory, 'b'))

        source_files = map(partial(os.path.join, self.zip_directory), self.zip_structure)
        map(lambda file: open(file, 'w+').write(file), source_files)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_directoryzip_integration(self):
        zipdirectory = DirectoryZipFile(self.zip_directory)
        zipdirectory.create_archive()
        zipdirectory.close()

        created_archive = ZipFile(zipdirectory.archive_path)
        archive_files = created_archive.namelist()

        self.assertEqual(archive_files, self.zip_structure)

    def test_zipdir(self):
        zip = DirectoryZipFile(self.zip_directory)
        zip.zipdir(self.zip_directory, self.zip_directory)
        zip.close()

        created_archive = ZipFile(zip.archive_path)
        archive_files = created_archive.namelist()

        self.assertEqual(archive_files, self.zip_structure)
