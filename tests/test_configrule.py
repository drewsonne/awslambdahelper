from awsconfig_lambdahelper.configrule import AWSConfigRule

def test_classinstantiation(mocker):
    with mocker.patch('awsconfig_lambdahelper.configrule.AWSConfigRule') as MockAWSConfigRule:
        instance = MockAWSConfigRule.return_value
        instance.find_violation.return_value = False

        AWSConfigRule(
            applicable_resources=["AWS::EC2::INSTANCE"]
        )


