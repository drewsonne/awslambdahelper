import ConfigParser
import zipfile

import argparse
import glob
import os
import shutil
import sys
import tempfile
import pip
from zipfile import ZipFile


class BundlerArgumentParser(argparse.ArgumentParser):
    """
    Parses command line arguments, and validates the integrity of the file paths and directories provided.
    """

    def __init__(self):
        """
        Add the cli argument schema
        """
        super(BundlerArgumentParser, self).__init__()
        self.add_argument('--directory', help='Path to the directory to bundle for AWS lambda.')
        self.add_argument('--requirements_name', default='requirements.txt',
                          help='Name of the requirements file in the target directory')

    def _parse_known_args(self, arg_strings, namespace):
        """
        Parse as the parent does, and then optionally raise an ArgumentException is :code:`--send-to-cfn` is missing
        :code:`--owner`.

        :param arg_strings: List of cli argument strings passed to the arg parser.
        :type arg_strings: list
        :param namespace: Namespace object, created by super :py:class:`argparse.ArgumentParser` namespace object.
        :type namespace: argparse.Namespace
        :returns:

                namespace(*argparse.Namespace*)
                    is the super :py:class:`argparse.ArgumentParser` namespace object, with the with the addition of the
                    arguments parse in this class.

                unparsed_args(*list[str]*)
                    are args which were not parsed by this ArgumentParser.
        """
        namespace, unparsed_args = super(BundlerArgumentParser, self)._parse_known_args(arg_strings, namespace)
        namespace.directory = self._full_path(namespace.directory)
        namespace.requirements_path = os.path.join(namespace.directory, namespace.requirements_name)

        directory_missing = self._test_missing_directory(namespace.directory)
        not_a_directory = self._test_not_a_directory(namespace.directory)
        missing_requirements = self._test_missing_requirements(namespace.requirements_path)

        if directory_missing or not_a_directory:
            directory_action = filter(lambda action: '--directory' in action.option_strings, self._actions).pop()
            raise argparse.ArgumentError(directory_action, directory_missing or not_a_directory)

        if missing_requirements:
            requirement_action = filter(lambda action: '--requirements_name' in action.option_strings,
                                        self._actions).pop()
            raise argparse.ArgumentError(requirement_action, missing_requirements)

        return namespace, unparsed_args

    @staticmethod
    def _test_missing_directory(target_directory):
        """
        If the specified directory is missing, return an error message

        :param target_directory: Fully qualified path to test
        :type target_directory: str
        :return: An error message, or False if the requirements file exists.
        :rtype: Union[str,bool]
        """
        if not os.path.exists(target_directory):
            return "Could not find `--directory={dir}`.".format(dir=target_directory)
        return False

    @staticmethod
    def _test_not_a_directory(target_directory):
        """
        If the specified path is not a directory, return an error message

        :param target_directory: Fully qualified path to test
        :type target_directory: str
        :return: An error message, or False if the requirements file exists.
        :rtype: Union[str,bool]
        """
        if not os.path.isdir(target_directory):
            return "`--directory={dir}` is not a directory.".format(dir=target_directory)
        return False

    @staticmethod
    def _test_missing_requirements(requirements_path):
        """
        If the requirements path does not exist, return an error method

        :param requirements_path: Fully qualified path to test.
        :type requirements_path: str
        :return: An error message, or False if the requirements file exists.
        :rtype: Union[str,bool]
        """
        if not os.path.exists(requirements_path):
            return "Could not find requirements file at `{path}`.".format(path=requirements_path)
        return False

    @staticmethod
    def _full_path(dir_):
        """
        Expand any '~', '../', or './' in the dir\_ path.

        :param dir_: A relative, home relative, or absolute path.
        :return: Fully Qualified path
        :rtype: str
        """
        if dir_[0] == '~' and not os.path.exists(dir_):
            dir_ = os.path.expanduser(dir_)
        return os.path.abspath(dir_)


class LambdahelperBundler(object):
    """
    Handler for the cli tool to archive code up for Lambda
    """

    def run(self, args=None):
        """
        Entrypoint for our bundler cli tool

        :param args: defaults to :py:data:`sys.argv[1:]`
        :return:
        """

        if args is None:
            args = sys.argv[1:]

        (self.target_directory,
         self.working_directory,
         self.requirements_path) = self.parse_args(args)

        for file in glob.glob(self.target_directory + os.path.sep + "*.py"):
            shutil.copy(file, self.working_directory)

        shutil.copy(self.requirements_path, self.working_directory)

        self.process_setup_cfg()

        pip.main([
            "install",
            "-t", self.working_directory,
            "-r", self.requirements_path
        ])

        self.create_zip()

    @staticmethod
    def parse_args(args):
        """
        Parse the args
        :param args:
        :return:
        """
        cli_args = BundlerArgumentParser().parse_args(args)
        return (
            cli_args.directory,
            tempfile.mkdtemp(),
            cli_args.requirements_path
        )

    def process_setup_cfg(self):
        """
        If the setup.cfg does not exist, or does not have an `[install`] section,
        create and append a `prefix= ` value.

        :param project_dir:
        :param working_directory:
        :return:
        """
        setup_cfg_path = os.path.join(self.target_directory, 'setup.cfg')
        temp_cfg_path = os.path.join(self.working_directory, 'setup.cfg')

        # If we already have a setup.cfg, modify it
        if os.path.exists(setup_cfg_path):
            self.update_setup_cfg(setup_cfg_path, temp_cfg_path)
        # If we don't, just write a blank file out.
        else:
            self.create_setup_cfg(temp_cfg_path)

    @staticmethod
    def update_setup_cfg(cfg_path, build_cfg_path):
        """
        Read the existing setup.cfg and add the install.prefix

        :param existing_cfg_path: Path to the existing setup.cfg
        :type existing_cfg_path: str
        :param temp_cfg_path:
        :type temp_cfg_path: str
        :return:
        """
        setup_cfg = ConfigParser.ConfigParser()
        setup_cfg.read(cfg_path)
        if 'install' not in setup_cfg.sections():
            setup_cfg.add_section('install')
        setup_cfg.set('install', 'prefix', '')

        with open(build_cfg_path, 'w') as fp:
            setup_cfg.write(fp)

    @staticmethod
    def create_setup_cfg(temp_cfg_path):
        """
        Create base setup.cfg file.

        :param cfg_path: Path to setup.cfg
        :type cfg_path: str
        :return:
        """
        with open(temp_cfg_path, 'w+') as fp:
            fp.write("""[install]\nprefix= """)


class DirectoryZipFile(ZipFile, object):
    """
    Handles the zipping of an entire directory
    """

    def __init__(self, target):
        zip_destination = target.rstrip(os.path.sep) + '.zip'

        ZipFile.__init__(self, zip_destination, 'w', zipfile.ZIP_DEFLATED)
        self.source_path = target
        self.archive_path = zip_destination

    def create_archive(self):
        """
        Given a target_directory to compress, and a working_directory to place the files in, compress them
        in a zip archive.

        :param target_directory:
        :param working_directory:
        :return:
        """
        self.zipdir(self.source_path, self.source_path.rstrip('/') + '/')

    def zipdir(self, path, zip_path_prefix):
        """
        Recursively walk our directory path, and add files to the zip archive.

        :param path: Path to walk which contains our files to be added to the zip archive.
        :param ziph: zipfile handler
        :type ziph: zipfile.ZipFile
        :param zip_path_prefix:
        :type basestring
        :return:
        """
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file_name in files:
                source_file = os.path.join(root, file_name)
                archive_file = source_file.replace(zip_path_prefix, '')
                print "    Adding file: '" + archive_file + "'"
                self.write(source_file, archive_file)


if __name__ == '__main__':
    LambdahelperBundler().run()
