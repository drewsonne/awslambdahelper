# -*- coding: utf-8 -*-
import unittest
from mock import MagicMock
from awslambdahelper import AWSConfigRule


class ConfigRuleTests(unittest.TestCase):
    def test_classinstantiation(self):
        AWSConfigRule(
            applicable_resources=["AWS::EC2::INSTANCE"]
        )

    def test_configcalltype(self):
        rule = AWSConfigRule(
            applicable_resources=["AWS::EC2::INSTANCE"]
        )
        rule.call_type = AWSConfigRule.CALL_TYPE_CONFIGURATION_CHANGE

        self.assertTrue(rule.is_config_change_call)

    def test_schedulecalltype(self):
        rule = AWSConfigRule(
            applicable_resources=["AWS::EC2::INSTANCE"]
        )
        rule.call_type = AWSConfigRule.CALL_TYPE_SCHEDULED

        self.assertTrue(rule.is_scheduled_call)

    def test_unimplemented_callbacks(self):
        rule = AWSConfigRule(
            applicable_resources=["AWS::EC2::INSTANCE"]
        )

        with self.assertRaises(NotImplementedError):
            rule.find_violation_config_change(config=None, rule_parameters=None)

        with self.assertRaises(NotImplementedError):
            rule.find_violation_scheduled(rule_parameters=None, accountid=None)

    def test_statichandler(self):
        class MockHandler(AWSConfigRule):
            APPLICABLE_RESOURCES = ['a', 'b']

        MockHandler.lambda_handler = MagicMock()

        MockHandler.handler({'event': None}, {'context': None})

        MockHandler.lambda_handler.assert_called_once_with(
            {'event': None}, {'context': None}
        )

    def test__aws_call(self):
        callable_payload = lambda: 'TestResponse'

        rule = AWSConfigRule()
        self.assertEqual(
            rule._aws_call(callable_payload),
            'TestResponse'
        )