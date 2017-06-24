import unittest

from mock import patch, MagicMock, call

from awslambdahelper.cli import zipdir


class MockZipFile(object):
    def __init__(self):
        self.files = []

    def write(self, fname):
        pass


class TestZipTestsTests(unittest.TestCase):
    @patch('os.walk')
    def test_zipdir(self, os_walk):
        os_walk.return_value = (('prefix/root', (), ('one', 'two')),)

        mock_write = MagicMock(None)
        zip = MockZipFile()
        zip.write = mock_write

        zipdir('path', zip, 'prefix')

        mock_write.assert_has_calls([
            call('prefix/root/one', '/root/one'),
            call('prefix/root/two', '/root/two')
        ])

        self.assertEqual(mock_write.call_count, 2)
