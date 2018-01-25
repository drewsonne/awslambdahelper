---------------
AWS Config Rule
---------------

AWS Config rules come in two flavours: *Scheduled* and *ConfigurationChange*.

*Scheduled* rules are invoked by AWS Config on a periodic basis as defined in your rule, and *ConfigurationChange*
rules are invoked by AWS Config when a configuration change occurs. Generally, you used scheduled rules for resources
which AWS Config `support directly <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html>`_,
and *ConfigurationChange* rules for
`additional resources types for AWS Config <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_.


Create a new class, write it in a function to be set as the lambda handler, and override either the
:code:`find_violation_scheduled(...)` function or :code:`find_violation_config_change(...)`.

~~~~~~~~~~~~~~~~~~~~~~~~~
Configuration Change Rule
~~~~~~~~~~~~~~~~~~~~~~~~~


>>> from awsconfig_lambdahelper.configrule import AWSConfigRule
>>> from awsconfig_lambdahelper.evaluation import CompliantEvaluation,NonCompliantEvaluation
>>>
>>> # A ConfigurationChange AWS config rule
>>> class MyCustomConfigurationChangeRule(AWSConfigRule):
...    def find_violation_config_change(self, config, rule_parameters):
...        rule_responses = apply_my_rule_to_a_resource(config)
...        response = []
...        for violation in rule_responses:
...            if violation['failed']:
...               response.append(
...                    NonCompliantEvaluation(
...                        Annotation="This failed because of a good reason."
...                    )
...              )
...            else:
...                # There's no need to set the resource id or type, as the library is aware of those
...                # values and will apply them automatically.
...                response.append(CompliantEvaluation())
...        return response
>>>
>>> # Lambda entrypoint
>>> def lambda_handler(event, context):
...    my_rule = MyCustomConfigurationChangeRule(
...        applicable_resources=["AWS::EC2::Instance"]
...    )
...    my_rule.lambda_handler(event, context)

~~~~~~~~~~~~~~
Scheduled Rule
~~~~~~~~~~~~~~


>>>    from awsconfig_lambdahelper.configrule import AWSConfigRule
>>>    from awsconfig_lambdahelper.evaluation import CompliantEvaluation,NonCompliantEvaluation
>>>    # A schedule AWS config rule
>>>    class MyCustomScheduledConfigRule(AWSConfigRule):
...        def find_violation_scheduled(self, rule_parameters, account_id):
...            rule_responses = apply_my_rules()
...            response = []
...            for violation in rule_responses:
...                if violation['failed']:
...                   response.append(
...                        # Scheduled rules are not in response to a config change, so you need to tell AWS Config what
...                        # resources you were looking at.
...                        CompliantEvaluation(
...                            ResourceType=violation['my_resource_type'],
...                            ResourceId=violation['my_resource_id']
...                        )
...                   )
...                else:
...                    response.append(
...                        NonCompliantEvaluation(
...                            ResourceType=violation['my_resource_type'],
...                            ResourceId=violation['my_resource_id'],
...                            Annotation="This failed because of a good reason."
...                        )
...                    )
...            return response
>>>
>>>    # Lambda entrypoint
>>>    def lambda_handler(event, context):
...       my_rule = MyCustomScheduledConfigRule(
...           applicable_resources=["AWS::EC2::Instance"]
...       )
...       my_rule.lambda_handler(event, context)


