from setuptools import setup, find_packages

setup(
    name='aws_lambdahelper',
    version='0.0.1',
    install_requires=['boto3'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-mock'],
    description='Handlers the nasty bits of AWS config rules',
    url='http://github.com/drew.sonne/aws_lambdahelper',
    author='Drew J. Sonne',
    author_email='drew.sonne@gmail.com',
    license='GLPG',
    packages=find_packages(),
    zip_safe=True
)
