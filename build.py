from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin('exec')

name = "awslambdahelper"
version = "1.1.0"
default_task = "publish"
authors = (Author("Drew J. Sonne", "drew.sonne@gmail.com", ),)
license = "LGLP"

RUNTIME_DEPENDENCIES = ['boto3']
BUILD_DEPENDENCIES = ['mock']


@init
def init(project):
    for dependency in RUNTIME_DEPENDENCIES:
        project.depends_on(dependency)

    for dependency in BUILD_DEPENDENCIES:
        project.build_depends_on(dependency)

    project.set_property('flake8_verbose_output', True)
    project.set_property("flake8_break_build", True)

    project.set_property("coverage_threshold_warn", 50)
    project.set_property("coverage_fork", True)

    project.set_property('distutils_upload_repository', 'https://pypi.python.org/pypi')

#
