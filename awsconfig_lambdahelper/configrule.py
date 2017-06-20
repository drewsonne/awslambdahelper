import json

import boto3


class AWSConfigRule(object):
    def __init__(self, applicable_resources):
        self.applicable_resources = applicable_resources

    def put_evaluations(self, *args, **kwargs):
        return boto3.client("config").put_evaluations(
            *args, **kwargs
        )

    def lambda_handler(self, event, context):
        invoking_event = json.loads(event["invokingEvent"])
        configuration_item = invoking_event["configurationItem"]
        rule_parameters = json.loads(event["ruleParameters"])

        result_token = "No token found."
        if "resultToken" in event:
            result_token = event["resultToken"]

        evaluation = self.evaluate_compliance(configuration_item, rule_parameters)

        self.put_evaluations(
            Evaluations=[
                {
                    "ComplianceResourceType":
                        configuration_item["resourceType"],
                    "ComplianceResourceId":
                        configuration_item["resourceId"],
                    "ComplianceType":
                        evaluation["compliance_type"],
                    "Annotation":
                        evaluation["annotation"],
                    "OrderingTimestamp":
                        configuration_item["configurationItemCaptureTime"]
                },
            ],
            ResultToken=result_token
        )

    def evaluate_compliance(self, configuration_item, rule_parameters):
        if configuration_item["resourceType"] not in self.applicable_resources:
            return {
                "compliance_type": "NOT_APPLICABLE",
                "annotation": "The rule doesn't apply to resources of type " +
                              configuration_item["resourceType"] + "."
            }

        violation = self.find_violation(
            configuration_item["configuration"].get("ipPermissions"),
            rule_parameters
        )

        if violation:
            return {
                "compliance_type": "NON_COMPLIANT",
                "annotation": violation
            }
        return {
            "compliance_type": "COMPLIANT",
            "annotation": "This resource is compliant with the rule."
        }

    def find_violation(self, param, rule_parameters):
        raise UnimplementedMethod(type(self).__name__ + ":find_violation() is not implemented.")


class UnimplementedMethod(Exception): pass
