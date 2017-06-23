import json

import boto3

from awslambdahelper.evaluation import NotApplicableEvaluation


class AWSConfigRule(object):
    CALL_TYPE_CONFIGURATION_CHANGE = 'ConfigurationItemChangeNotification'
    CALL_TYPE_SCHEDULED = 'ScheduledNotification'

    def __init__(self, applicable_resources):
        self.applicable_resources = applicable_resources
        self.call_type = None

    @property
    def is_config_change_call(self):
        return self.call_type == self.CALL_TYPE_CONFIGURATION_CHANGE

    @property
    def is_scheduled_call(self):
        return self.call_type == self.CALL_TYPE_SCHEDULED

    @staticmethod
    def put_evaluations(*args, **kwargs):
        return boto3.client("config").put_evaluations(
            *args, **kwargs
        )

    def lambda_handler(self, event, context):
        """
        See Event Attributes in
        http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_example-events.html \
        #w2ab1c13c33c27c15c15
        :param event:
        :param context:
        :return:
        """
        invoking_event = json.loads(event["invokingEvent"])
        rule_parameters = json.loads(event["ruleParameters"])

        self.call_type = invoking_event['messageType']

        result_token = "No token found."
        if "resultToken" in event:
            result_token = event["resultToken"]

        evaluations = []

        if self.is_config_change_call:

            configuration_item = invoking_event["configurationItem"]
            evaluation_responses = self.evaluate_compliance(
                config=configuration_item,
                rule_parameters=rule_parameters,
                event=event
            )

            for evaluation_response in evaluation_responses:
                evaluation = evaluation_response.append(
                    ResourceType=configuration_item["resourceType"],
                    ResourceId=configuration_item["resourceId"],
                    OrderingTimestamp=configuration_item["configurationItemCaptureTime"]
                ).to_dict()
                evaluations.append(evaluation)
        else:
            evaluation_responses = self.evaluate_compliance(
                rule_parameters=rule_parameters,
                event=event
            )

            for evaluation_response in evaluation_responses:
                evaluations.append(evaluation_response.append(
                    OrderingTimestamp=invoking_event["notificationCreationTime"]
                ).to_dict())

        chunk_size = 100
        for evaluation_chunk in range(0, len(evaluations), chunk_size):
            self.put_evaluations(
                Evaluations=evaluations[evaluation_chunk:evaluation_chunk + chunk_size],
                ResultToken=result_token
            )

    def evaluate_compliance(self, rule_parameters, event, config=None):
        if self.is_config_change_call:
            if config["resourceType"] not in self.applicable_resources:
                return [NotApplicableEvaluation(
                    ResourceType=config["resourceType"],
                )]

            violations = self.find_violation_config_change(
                rule_parameters=rule_parameters,
                config=config
            )
        else:
            violations = self.find_violation_scheduled(
                rule_parameters=rule_parameters,
                accountid=event['accountId']
            )

        return violations

    def find_violation_config_change(self, rule_parameters, config):
        raise UnimplementedMethod(type(self).__name__ + ":find_violation_config_change() is not implemented.")

    def find_violation_scheduled(self, rule_parameters, accountid):
        raise UnimplementedMethod(type(self).__name__ + ":find_violation_scheduled() is not implemented.")


class UnimplementedMethod(Exception):
    pass
