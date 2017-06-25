# -*- coding: utf-8 -*-
import unittest

from awslambdahelper import AWSConfigEvaluation, InsufficientDataEvaluation, NonCompliantEvaluation


class TestEvaluations(unittest.TestCase):
    def test_missingtimestamp(self):
        evaluation = AWSConfigEvaluation(AWSConfigEvaluation.TYPE_NON_COMPLIANT, 'debug')
        payload = evaluation.to_dict()
        self.assertRegexpMatches(payload['OrderingTimestamp'], r"\d{4}-\d{2}-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d+Z")

    def test_existingtimestamp(self):
        evaluation = AWSConfigEvaluation(
            AWSConfigEvaluation.TYPE_NON_COMPLIANT,
            Annotation='debug',
            OrderingTimestamp='timestamp'
        )
        payload = evaluation.to_dict()
        self.assertEqual(payload['OrderingTimestamp'], 'timestamp')

    def test_insufficientdataevaluation(self):
        evaluation = InsufficientDataEvaluation(
            Annotation='testing-annotation',
            ResourceId='resource-id',
            ResourceType='resource-type',
            OrderingTimestamp='ordering-timestamp'
        )

        self.assertDictEqual(evaluation.to_dict(), {
            'Annotation': 'testing-annotation',
            'ComplianceResourceId': 'resource-id',
            'ComplianceResourceType': 'resource-type',
            'ComplianceType': 'INSUFFICIENT_DATA',
            'OrderingTimestamp': 'ordering-timestamp'

        })

    def test_non_compliant_evaluation(self):
        evaluation = NonCompliantEvaluation(
            Annotation='non-compliantevaluation',
            OrderingTimestamp='my-timestamp'
        )

        self.assertDictEqual(evaluation.to_dict(), {
            'Annotation': 'non-compliantevaluation',
            'ComplianceResourceId': None,
            'ComplianceResourceType': None,
            'ComplianceType': 'NON_COMPLIANT',
            'OrderingTimestamp': 'my-timestamp'
        })
