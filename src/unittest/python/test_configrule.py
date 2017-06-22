import pytest


def test_classinstantiation(mocker):
    from awslambdahelper.configrule import AWSConfigRule

    AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )


def test_configcalltype():
    from awslambdahelper.configrule import AWSConfigRule

    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )
    rule.call_type = AWSConfigRule.CALL_TYPE_CONFIGURATION_CHANGE

    assert rule.is_config_change_call


def test_schedulecalltype():
    from awslambdahelper.configrule import AWSConfigRule

    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )
    rule.call_type = AWSConfigRule.CALL_TYPE_SCHEDULED

    assert rule.is_scheduled_call


def test_unimplemented_callbacks():
    from awslambdahelper.configrule import AWSConfigRule, UnimplementedMethod

    rule = AWSConfigRule(
        applicable_resources=["AWS::EC2::INSTANCE"]
    )

    with pytest.raises(UnimplementedMethod):
        rule.find_violation_config_change(config=None, rule_parameters=None)

    with pytest.raises(UnimplementedMethod):
        rule.find_violation_scheduled(rule_parameters=None, accountid=None)
