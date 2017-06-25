# -*- coding: utf-8 -*-
import unittest
from mock import patch, call, MagicMock, mock_open
from awslambdahelper.cli import SetupCfgFile


class TestCliCfgManipulation(unittest.TestCase):
    def test_instantiation(self):
        setup = SetupCfgFile('setup', 'temp')

        self.assertEqual(setup.setup_cfg, 'setup')
        self.assertEqual(setup.temp_setup_cfg, 'temp')

    @patch('os.path.exists')
    def test_loadexists(self, path_exists):
        setup = SetupCfgFile('setup', 'temp')

        setup.read = MagicMock()
        path_exists.return_value = True
        setup.load()

        setup.read.assert_called_once_with('setup')

    @patch('os.path.exists')
    def test_loadnotexist(self, path_exists):
        setup = SetupCfgFile('setup', 'temp')

        setup.read = MagicMock()
        path_exists.return_value = False
        setup.load()

        setup.read.assert_not_called()

    @patch('ConfigParser.ConfigParser.write')
    def test_writeexistinginstall(self, super_write):
        """
        Test the case where we already have 'install' entry in our setup.cfg
        """
        setup = SetupCfgFile('setup', 'temp')
        setup.sections = MagicMock()
        setup.set = MagicMock()
        setup.add_section = MagicMock()

        setup.sections.return_value = ['install']

        m = mock_open()
        with patch('__builtin__.open', m):
            setup.write()

        setup.add_section.assert_not_called()
        setup.set.assert_called_once_with('install', 'prefix', '')
        m.assert_called_once_with('temp')

    @patch('ConfigParser.ConfigParser.write')
    def test_writemissinginstall(self, super_write):
        """
        Test the case where we already have 'install' entry in our setup.cfg
        """
        setup = SetupCfgFile('setup', 'temp')
        setup.sections = MagicMock()
        setup.set = MagicMock()
        setup.add_section = MagicMock()

        setup.sections.return_value = []

        m = mock_open()
        with patch('__builtin__.open', m):
            setup.write()

        setup.add_section.assert_called_once_with('install')
        setup.set.assert_called_once_with('install', 'prefix', '')
        m.assert_called_once_with('temp')
