import ConfigParser
import argparse
import glob
import os
import shutil
import sys
import tempfile
import pip
import zipfile


class BundlerArgumentParser(argparse.ArgumentParser):
    """
    Parses command line arguments, and validates the integrity of the file paths and directories provided.
    """

    def __init__(self):
        """

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


def main(args=None):
    """
    Entrypoint for our bundler cli tool

    :param args: defaults to :py:data:`sys.argv[1:]`
    :return:
    """

    if args is None:
        args = sys.argv[1:]

    cli_args = BundlerArgumentParser().parse_args(args)

    target_directory = cli_args.directory
    requirements_path = cli_args.requirements_path

    # Create temporary working directory
    working_directory = tempfile.mkdtemp()
    print "working in: " + working_directory

    for file in glob.glob(target_directory + os.path.sep + "*.py"):
        shutil.copy(file, working_directory)

    shutil.copy(requirements_path, working_directory)

    process_setup_cfg(target_directory, working_directory)

    pip.main([
        "install",
        "-t", working_directory,
        "-r", requirements_path
    ])

    create_zip(target_directory, working_directory)


def create_zip(target_directory, working_directory):
    """
    Given a target_directory to compress, and a working_directory to place the files in, compress them
    in a zip archive.

    :param target_directory:
    :param working_directory:
    :return:
    """
    zip_destination = target_directory.rstrip(os.path.sep) + '.zip'
    print "Creating zip archive: '" + zip_destination + "'"

    zipf = zipfile.ZipFile(zip_destination, 'w', zipfile.ZIP_DEFLATED)
    zipdir(working_directory, zipf, working_directory.rstrip('/') + '/')

    zipf.close()


def zipdir(path, ziph, zip_path_prefix):
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
        for file in files:
            source_file = os.path.join(root, file)
            archive_file = source_file.replace(zip_path_prefix, '')
            print "    Adding file: '" + archive_file + "'"
            ziph.write(source_file, archive_file)


def process_setup_cfg(project_dir, working_directory):
    """
    If the setup.cfg does not exist, or does not have an `[install`] section,
    create and append a `prefix= ` value.

    :param project_dir:
    :param working_directory:
    :return:
    """
    setup_cfg_path = os.path.join(project_dir, 'setup.cfg')
    temporary_cfg_path = os.path.join(working_directory, 'setup.cfg')

    # If we already have a setup.cfg, modify it
    if os.path.exists(setup_cfg_path):
        setup_cfg = ConfigParser.ConfigParser()
        setup_cfg.read(setup_cfg_path)
        if 'install' not in setup_cfg.sections():
            setup_cfg.add_section('install')
        setup_cfg.set('install', 'prefix', '')

        with open(temporary_cfg_path, 'w') as fp:
            setup_cfg.write(fp)
    # If we don't, just write a blank file out.
    else:
        with open(temporary_cfg_path, 'w+') as fp:
            fp.write("""[install]\nprefix= """)


if __name__ == '__main__':
    main()
