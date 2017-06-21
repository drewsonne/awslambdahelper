# aws_lambdahelper
Abstracts the more mundane aspects of lambda resources


## Usage

### Installation

__Pip__
```shell
$ pip install aws_lambdahelper
```

__Bundled__
```python
# setup.py
from setuptools import setup

setup(
    name='my_custom_config_rule',
    install_requires=['aws_lambda_helper'],
    ...
)
```

### AWS Config Rule

Create a new class, write it in a function to be set as the lambda handler, and override either the 
`find_violation_scheduled(...)` function or `find_violation_config_change(...)`.

#### Configuration Change Rule

```python
from awsconfig_lambdahelper.configrule import AWSConfigRule
from awsconfig_lambdahelper.evaluation import CompliantEvaluation,NonCompliantEvaluation


# A schedule AWS config rule
class MyCustomConfigurationChangeRule(AWSConfigRule):
    def find_violation_config_change(self, config, rule_parameters):

        rule_responses = apply_my_rule_to_a_resource(config)
        
        response = []
        for violation in rule_responses:
            if violation['failed']:
               response.append(
                    # There's no need to set the resource id or type, as the library is aware of those
                    # values and will apply them automatically.
                    CompliantEvaluation()
               ) 
            else:
                response.append(
                    NonCompliantEvaluation(
                        Annotation="This failed because of a good reason."
                    )
                )
        
        return response

# Lambda entrypoint
def lambda_handler(event, context):

    my_rule = MyCustomConfigurationChangeRule(
        applicable_resources=["AWS::EC2::Instance"]
    )
    my_rule.lambda_handler(event, context)


```


#### Scheduled Rule

```python

from awsconfig_lambdahelper.configrule import AWSConfigRule
from awsconfig_lambdahelper.evaluation import CompliantEvaluation,NonCompliantEvaluation


# A schedule AWS config rule
class MyCustomScheduledConfigRule(AWSConfigRule):
    def find_violation_scheduled(self, ruleParameters, accountId):

        rule_responses = apply_my_rules()
        
        response = []
        for violation in rule_responses:
            if violation['failed']:
               response.append(
                    # Scheduled rules are not in response to a config change, so you need to tell AWS Config what
                    # resources you were looking at.
                    CompliantEvaluation(
                        ResourceType=violation['my_resource_type'],
                        ResourceId=violation['my_resource_id']
                    )
               ) 
            else:
                response.append(
                    NonCompliantEvaluation(
                        ResourceType=violation['my_resource_type'],
                        ResourceId=violation['my_resource_id'],
                        Annotation="This failed because of a good reason."
                    )
                )
        
        return response

# Lambda entrypoint
def lambda_handler(event, context):

    my_rule = MyCustomScheduledConfigRule(
        applicable_resources=["AWS::EC2::Instance"]
    )
    my_rule.lambda_handler(event, context)

```