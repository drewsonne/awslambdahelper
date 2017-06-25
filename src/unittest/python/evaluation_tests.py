import unittest

from awslambdahelper import AWSConfigEvaluation


class TestEvaluations(unittest.TestCase):
    def test_missingtimestamp(self):
        evaluation = AWSConfigEvaluation(AWSConfigEvaluation.TYPE_NON_COMPLIANT, 'debug')
        payload = evaluation.to_dict()
        self.assertRegexpMatches(payload['OrderingTimestamp'],r"\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d+Z")
