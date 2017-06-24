import unittest
from awslambdahelper import AWSConfigRule, UnimplementedMethod

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

        with self.assertRaises(UnimplementedMethod):
            rule.find_violation_config_change(config=None, rule_parameters=None)

        with self.assertRaises(UnimplementedMethod):
            rule.find_violation_scheduled(rule_parameters=None, accountid=None)
