# -*- coding: utf-8 -*-
from pybuilder.core import use_plugin, init, Author

_version = ('1', '1', '14')

use_plugin('exec')
use_plugin("python.core")
use_plugin("python.flake8")
use_plugin('python.sphinx')
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin("python.distutils")
use_plugin("source_distribution")
use_plugin("python.install_dependencies")

name = "awslambdahelper"
version = ".".join(_version)
default_task = "publish"
authors = (Author("Drew J. Sonne", "drew.sonne@gmail.com", ),)
license = "LGLP"
url = "http://lambda.awshelpers.com/"

RUNTIME_DEPENDENCIES = ['boto3', 'backoff']
BUILD_DEPENDENCIES = ['sphinx_rtd_theme', 'mock', 'coverage', 'wheel']


@init
def init(project):
    for dependency in RUNTIME_DEPENDENCIES:
        project.depends_on(dependency)

    for dependency in BUILD_DEPENDENCIES:
        project.build_depends_on(dependency)

    project.set_property('flake8_verbose_output', True)
    project.set_property("flake8_break_build", True)

    project.set_property("coverage_threshold_warn", 75)

    project.depends_on("pip", ">=7.1")
    project.depends_on("setuptools", "~=35.0")

    project.get_property("source_dist_ignore_patterns").append(".cache")
    project.get_property("source_dist_ignore_patterns").append(".idea")
    project.get_property("source_dist_ignore_patterns").append(".direnv")
    project.get_property("source_dist_ignore_patterns").append(".project")
    project.get_property("source_dist_ignore_patterns").append(".pydevproject")
    project.get_property("source_dist_ignore_patterns").append(".settings")

    project.set_property('distutils_upload_repository', 'https://upload.pypi.org/legacy/')
    project.set_property("distutils_description_overwrite", True)
    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_use_setuptools", True)
    project.set_property("distutils_classifiers", [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'])
