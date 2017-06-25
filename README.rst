=====================
awslambdahelper 1.1.8
=====================

.. image:: https://www.quantifiedcode.com/api/v1/project/bb53f496a1cc45f780342fc973270298/badge.svg
  :target: https://www.quantifiedcode.com/app/project/bb53f496a1cc45f780342fc973270298
  :alt: Code issues
.. image:: https://codecov.io/github/drewsonne/awslambdahelper/coverage.svg?branch=master
  :target: https://codecov.io/github/drewsonne/awslambdahelper?branch=master
.. image:: https://travis-ci.org/drewsonne/awslambdahelper.svg?branch=master
  :target: https://travis-ci.org/drewsonne/awslambdahelper
.. image:: https://img.shields.io/pypi/v/awslambdahelper.svg
  :target: https://pypi.python.org/pypi/awslambdahelper

Abstracts the more mundane aspects of lambda resources

A lot of boilerplate code is required to implemented lambda's for AWS
Config and custom Cloudformation resources. We can abstract this away
and wrap our rule in data structures to improve development and
encourage a particular structure.

------------
Installation
------------

.. code-block:: bash

  $ pip install awslambdahelper


----------
QuickStart
----------

~~~~~~~~~~~~~~~~~~~~~
Create a Python class
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  # my_lambda_code.py
  from awslambdahelper import AWSConfigRule

  class MyConfigRule(AWSConfigRule):
      def find_violation_config_change(self, config, rule_parameters):
        return [NonCompliantEvaluation(
          Annotation="This failed because it is only a demo."
        )]


~~~~~~~~~~~~~~~~~~~~~~~~
Setup AWS Lambda handler
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  >>> import boto3
  >>> boto3.client('lambda').create_function(
    Handler = "my_lambda_code.MyConfigRule.handler'
  )

~~~~~~~~~~~~~~~~~~~~~~
Create AWS Config Rule
~~~~~~~~~~~~~~~~~~~~~~

`Getting Started with Custom Rules <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_getting-started.html>`_.


That's it! For a more indepth guide, `read the docs <http://awslambdahelper.readthedocs.io/en/latest/>`_.
