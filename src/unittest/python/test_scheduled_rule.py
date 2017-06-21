from unittest import TestCase

import pytest, json

from awslambdahelper.configrule import AWSConfigRule
from awslambdahelper.evaluation import CompliantEvaluation


@pytest.mark.parametrize('lambda_event,put_evaluations_response', [
    (
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
            },
            # Response
            {
                "Evaluations": [{
                    "OrderingTimestamp": "2016-07-13T21:50:00.373Z",
                    "ComplianceResourceId": "i-00000000",
                    "ComplianceResourceType": "AWS::EC2::Instance",
                    "Annotation": "This resource is compliant with the rule.",
                    "ComplianceType": "COMPLIANT"
                }],
                "ResultToken": "myResultToken"
            }
    )
])
def test_schedule_event(mocker, lambda_event, put_evaluations_response):
    class MockScheduleRule(AWSConfigRule):
        def find_violation_scheduled(self, rule_parameters, accountid):
            return [CompliantEvaluation(
                ResourceType="AWS::EC2::Instance",
                ResourceId="i-00000000"
            )]

    mock_rule = MockScheduleRule(
        applicable_resources=["AWS::EC2::Instance"]
    )
    put_evaluations_stub = mocker.stub(name='put_evaluations_stub')
    mock_rule.put_evaluations = put_evaluations_stub

    mock_rule.lambda_handler(
        event=lambda_event,
        context=None
    )

    put_evaluations_stub.assert_called_once_with(**put_evaluations_response)
