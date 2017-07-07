------------
[unreleased]
------------

---------------------
[1.1.13] - 07-07-2017
---------------------

~~~~~
Added
~~~~~

 - :code:`awslambdahelper.AWSConfigRule._aws_call` which handles API backoffs if there are rate limiting exceptions.

---------------------
[1.1.12] - 26-06-2017
---------------------

~~~~~~~
Changed
~~~~~~~

 - Fixed a bug where :code:`lambdahelper-bundler` was not archiving the zip to the correct place

---------------------
[1.1.10] - 25-06-2017
---------------------

~~~~~~~
Changed
~~~~~~~

 - Expanded test coverage
 - Expanded the documentation
 - Refactored the cli tool to improve test coverage

--------------------
[1.1.6] - 24-06-2017
--------------------

~~~~~~~
Changed
~~~~~~~

 - Expanded test coverage
 - Expanded the documentation and added a short user guide.
 - Restructured the module to export :py:class:`~awslambdahelper.AWSConfigRule`, :py:class:`~awslambdahelper.CompliantEvaluation`, :py:class:`~awslambdahelper.NonCompliantEvaluation`, :py:class:`~awslambdahelper.NotApplicableEvaluation`, :py:class:`~awslambdahelper.InsufficientDataEvaluation`
