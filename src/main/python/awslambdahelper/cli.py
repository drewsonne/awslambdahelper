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
    def __init__(self):
        super(BundlerArgumentParser, self).__init__()
        self.add_argument('--directory', help='Path to the directory to bundle for AWS lambda.')
        self.add_argument('--requirements_name', default='requirements.txt',
                          help='Name of the requirements file in the target directory')

    def _parse_known_args(self, arg_strings, namespace):
        """
        Parse as the parent does, and then optionally raise an ArgumentException is --send-to-cfn is missing --owner.
        :param arg_strings:
        :param namespace:
        :return:
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
        if not os.path.exists(target_directory):
            return "Could not find `--directory={dir}`.".format(dir=target_directory)
        return False

    @staticmethod
    def _test_not_a_directory(target_directory):
        if not os.path.isdir(target_directory):
            return "`--directory={dir}` is not a directory.".format(dir=target_directory)
        return False

    @staticmethod
    def _test_missing_requirements(requirements_path):
        if not os.path.exists(requirements_path):
            return "Could not find requirements file at `{path}`.".format(path=requirements_path)
        return False

    @staticmethod
    def _full_path(dir_):
        if dir_[0] == '~' and not os.path.exists(dir_):
            dir_ = os.path.expanduser(dir_)
        return os.path.abspath(dir_)


def main(args=sys.argv[1:]):
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
    zip_destination = target_directory.rstrip(os.path.sep) + '.zip'
    print "Creating zip archive: '" + zip_destination + "'"

    zipf = zipfile.ZipFile(zip_destination, 'w', zipfile.ZIP_DEFLATED)
    zipdir(working_directory, zipf, working_directory.rstrip('/') + '/')

    zipf.close()


def zipdir(path, ziph, zip_path_prefix):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            source_file = os.path.join(root, file)
            archive_file = source_file.replace(zip_path_prefix, '')
            print "    Adding file: '" + archive_file + "'"
            ziph.write(source_file, archive_file)


def process_setup_cfg(project_dir, working_directory):
    if sys.platform == 'darwin':
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
