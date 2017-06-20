import json

import pytest

from awsconfig_lambdahelper.configrule import AWSConfigRule


@pytest.mark.parametrize('lambda_event', [
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
                "resourceType": "AWS::EC2::Instance", "tags": {"Foo": "Bar"},
                "relationships": [
                    {
                        "resourceId": "eipalloc-00000000",
                        "resourceType": "AWS::EC2::EIP",
                        "name": "Is attached to ElasticIp"
                    }
                ],
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
    {
        "invokingEvent": json.dumps({
            "awsAccountId": "123456789012",
            "notificationCreationTime": "2016-07-13T21:50:00.373Z",
            "messageType": "ScheduledNotification",
            "recordVersion": "1.0"
        }),
        "ruleParameters": json.dumps({
            "myParameterKey": "myParameterValue"
        }),
        "resultToken": "myResultToken",
        "eventLeftScope": False,
        "executionRoleArn": "arn:aws:iam::123456789012:role/config-role",
        "configRuleArn": "arn:aws:config:us-east-1:123456789012:config-rule/config-rule-0123456",
        "configRuleName": "periodic-config-rule",
        "configRuleId": "config-rule-6543210",
        "accountId": "123456789012",
        "version": "1.0"
    }
])
def test_classinstantiation(mocker, lambda_event):
    with mocker.patch('awsconfig_lambdahelper.configrule.AWSConfigRule') as MockAWSConfigRule:
        instance = MockAWSConfigRule.return_value
        instance.find_violation.return_value = False

        mock_rule = AWSConfigRule(
            applicable_resources=["AWS::AutoScaling::AutoScalingGroup"]
        )

        mock_rule.lambda_handler(
            event=lambda_event,
            context=None
        )
