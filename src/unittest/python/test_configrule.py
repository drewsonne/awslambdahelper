import pytest

from awslambdahelper.configrule import AWSConfigRule, UnimplementedMethod


def test_classinstantiation(mocker):
    AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )


def test_configcalltype():
    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )
    rule.call_type = AWSConfigRule.CALL_TYPE_CONFIGURATION_CHANGE

    assert rule.is_config_change_call


def test_schedulecalltype():
    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )
    rule.call_type = AWSConfigRule.CALL_TYPE_SCHEDULED

    assert rule.is_scheduled_call


def test_unimplemented_callbacks():
    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )

    with pytest.raises(UnimplementedMethod):
        rule.find_violation_config_change(config=None, rule_parameters=None)

    with pytest.raises(UnimplementedMethod):
        rule.find_violation_scheduled(rule_parameters=None, accountid=None)
