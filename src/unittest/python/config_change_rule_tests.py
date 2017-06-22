import json, unittest

from mock import MagicMock

from awslambdahelper.configrule import AWSConfigRule
from awslambdahelper.evaluation import CompliantEvaluation


class TestConfigChangeRuleTests(unittest.TestCase):
    def setUp(self):
        self.parameters = [
            (
                # AWS Lambda event payload. Request from AWS Config
                {
                    "invokingEvent": json.dumps({
                        "configurationItem": {
                            "configurationItemCaptureTime": "2016-02-17T01:36:34.043Z",
                            "awsAccountId": "123456789012",
                            "configurationItemStatus": "OK",
                            "resourceId": "i-00000000",
                            "ARN": "arn:aws:ec2:us-east-1:123456789012:instance/i-00000000",
                            "awsRegion": "us-east-1",
                            "availabilityZone": "us-east-1a",
                            "resourceType": "AWS::EC2::Instance",
                            "tags": {"Foo": "Bar"},
                            "relationships": [{
                                "resourceId": "eipalloc-00000000",
                                "resourceType": "AWS::EC2::EIP",
                                "name": "Is attached to ElasticIp"
                            }],
                            "configuration": {
                                "foo": "bar"
                            }
                        },
                        "messageType": "ConfigurationItemChangeNotification"
                    }),
                    "ruleParameters": json.dumps({
                        "myParameterKey": "myParameterValue"
                    }),
                    "resultToken": "myResultToken",
                    "eventLeftScope": False,
                    "executionRoleArn": "arn:aws:iam::123456789012:role/config-role",
                    "configRuleArn": "arn:aws:config:us-east-1:123456789012:config-rule/config-rule-0123456",
                    "configRuleName": "change-triggered-config-rule",
                    "configRuleId": "config-rule-0123456",
                    "accountId": "123456789012",
                    "version": "1.0"
                },
                # Response
                {
                    "Evaluations": [{
                        "OrderingTimestamp": "2016-02-17T01:36:34.043Z",
                        "ComplianceResourceId": "i-00000000",
                        "ComplianceResourceType": "AWS::EC2::Instance",
                        "Annotation": "This resource is compliant with the rule.",
                        "ComplianceType": "COMPLIANT"
                    }],
                    "ResultToken": "myResultToken"
                }
            ), (
                # AWS Lambda event payload. Request from AWS Config
                {
                    "invokingEvent": json.dumps({
                        "configurationItem": {
                            "configurationItemCaptureTime": "2016-02-17T01:36:34.043Z",
                            "awsAccountId": "123456789012",
                            "configurationItemStatus": "OK",
                            "resourceId": "sg-00000000",
                            "ARN": "arn:aws:ec2:us-east-1:123456789012:security-group/sg-00000000",
                            "awsRegion": "us-east-1",
                            "availabilityZone": "us-east-1a",
                            "resourceType": "AWS::EC2::SecurityGroup",
                            "tags": {"Foo": "Bar"},
                            "configuration": {
                                "foo": "bar"
                            }
                        },
                        "messageType": "ConfigurationItemChangeNotification"
                    }),
                    "ruleParameters": json.dumps({
                        "myParameterKey": "myParameterValue"
                    }),
                    "resultToken": "myResultToken",
                    "eventLeftScope": False,
                    "executionRoleArn": "arn:aws:iam::123456789012:role/config-role",
                    "configRuleArn": "arn:aws:config:us-east-1:123456789012:config-rule/config-rule-0123456",
                    "configRuleName": "change-triggered-config-rule",
                    "configRuleId": "config-rule-0123456",
                    "accountId": "123456789012",
                    "version": "1.0"
                },
                # Response
                {
                    "Evaluations": [{
                        "OrderingTimestamp": "2016-02-17T01:36:34.043Z",
                        "ComplianceResourceId": "sg-00000000",
                        "ComplianceResourceType": "AWS::EC2::SecurityGroup",
                        "Annotation": "The rule doesn't apply to resources of type AWS::EC2::SecurityGroup.",
                        "ComplianceType": "NOT_APPLICABLE"
                    }],
                    "ResultToken": "myResultToken"
                }
            )
        ]

    # @pytest.mark.parametrize('lambda_event,put_evaluations_response', )
    def test_configchangeevent(self):
        class MockConfigRule(AWSConfigRule):
            def find_violation_config_change(self, config, rule_parameters):
                return [CompliantEvaluation()]

        mock_rule = MockConfigRule(
            applicable_resources=["AWS::EC2::Instance"]
        )

        for lambda_event, put_evaluations_response in self.parameters:
            mock_rule.put_evaluations = MagicMock()

            mock_rule.lambda_handler(
                event=lambda_event,
                context=None
            )

            mock_rule.put_evaluations.assert_called_once_with(**put_evaluations_response)
