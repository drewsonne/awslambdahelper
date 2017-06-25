import abc
import json, boto3

from awslambdahelper.evaluation import AWSConfigEvaluation


class AWSConfigRule(object):
    """
    Defines the business logic for processing either scheduled or config change AWS Config rules
    """
    #: Specifies an AWS Config Rule which is triggered by a resource configuration
    CALL_TYPE_CONFIGURATION_CHANGE = 'ConfigurationItemChangeNotification'
    #: Specifies an AWS Config Rule which is triggered on a scheduled basis
    CALL_TYPE_SCHEDULED = 'ScheduledNotification'
    #: List of resources which this rule can evaluate. Only application for ConfigurationChange rules.
    APPLICABLE_RESOURCES = []

    @classmethod
    def handler(cls, event, context):
        """
        Allow a single entrypoint without extra boilerplate code.

        >>> from awslambdahelper import AWSConfigRule,InsufficientDataEvaluation
        >>> class MyAwesomeRule(AWSConfigRule):
        ...     APPLICABLE_RESOURCES = ["AWS::EC2::Instance"]
        ...     def find_violation_config_change(self, rule_parameters, config):
        ...         return [InsufficientDataEvaluation()]
        >>>
        >>> # The entrypoint for lambda would be set as "file_name.MyAwesomeRule.handler"

        :param event: See `Event Attributes
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_example-events.html#w2ab1c13c33c27c15c15>`_
            in the AWS Config Developer guide.
        :param context: See `Context Object <http://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html#python-context-object-methods>`_
        :return:
        """
        rule = cls(cls.APPLICABLE_RESOURCES)
        rule.lambda_handler(event, context)

    def __init__(self, applicable_resources=None):
        """
        If this rule is for handling ConfigurationChange events, then the "Applicable Resources" attribute must be set.
        If this is for handling Scheduled events, then no item is required.

        :param applicable_resources: A list of AWS resources which this rule evaluates. Only applicable for
            Configuration Change rules, and not Scheduled rules. See `Evaluating Additional Resource Types
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_,
            and
            `Supported AWS Resource Types <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources>`_.
        :type applicable_resources: Union[List,Tuple]
        """
        if applicable_resources is None:
            self.applicable_resources = self.APPLICABLE_RESOURCES
        else:
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
        .. deprecated:: 1.1.4
            Use :py:meth:`~awslambdahelper.AWSConfigRule.handler`
        """
        invoking_event = json.loads(event["invokingEvent"])
        if 'ruleParameters' in event:
            rule_parameters = json.loads(event["ruleParameters"])
        else:
            rule_parameters = {}

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
                evaluation = evaluation_response.set(
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
                evaluations.append(evaluation_response.set(
                    OrderingTimestamp=invoking_event["notificationCreationTime"]
                ).to_dict())

        chunk_size = 100
        for evaluation_chunk in range(0, len(evaluations), chunk_size):
            self.put_evaluations(
                Evaluations=evaluations[evaluation_chunk:evaluation_chunk + chunk_size],
                ResultToken=result_token
            )

    def evaluate_compliance(self, rule_parameters, event, config=None):
        """
        A facade to delegate the event to either the :py:meth:`~awslambdahelper.AWSConfigRule.find_violation_config_change`, or
        :py:meth:`~awslambdahelper.AWSConfigRule.find_violation_scheduled`.

        :param rule_parameters: A list of key/pairs which are to be provided to the rule.
        :type: dict
        :param event:
        :param config:
        :return:
        """
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
        """
        Place holder function for configuration change rules. Needs to be overriden by super class.

        :raises: NotImplementedError
        :param rule_parameters:
        :param config:
        :return: None
        """
        raise NotImplementedError(type(self).__name__ + ":find_violation_config_change() is not implemented.")

    def find_violation_scheduled(self, rule_parameters, accountid):
        """
        Place holder function for configuration change rules. Needs to be overriden by super class.

        :param rule_parameters:
        :param accountid:
        :return: None
        """
        raise NotImplementedError(type(self).__name__ + ":find_violation_scheduled() is not implemented.")


class CompliantEvaluation(AWSConfigEvaluation):
    """
    A rule is compliant if all of the resources that the rule evaluates comply with it,
    """

    def __init__(self, Annotation="This resource is compliant with the rule.", ResourceType=None,
                 ResourceId=None,
                 OrderingTimestamp=None):
        """

        :param Annotation: An explanation to attach to the evaluation result. Shown in the AWS Config Console.
        :type Annotation: str
        :param ResourceType:  A list of AWS resources which this rule evaluates. See `Evaluating Additional Resource Types
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_,
            and
            `Supported AWS Resource Types <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources>`_.
        :type ResourceType: str
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        """
        super(CompliantEvaluation, self).__init__(
            AWSConfigEvaluation.TYPE_COMPLIANT,
            Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp,
        )


class NonCompliantEvaluation(AWSConfigEvaluation):
    """
    A rule is noncompliant if any of these resources do not comply.
    """

    def __init__(self, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        """

        :param Annotation: An explanation to attach to the evaluation result. Shown in the AWS Config Console.
        :type Annotation: str
        :param ResourceType:  A list of AWS resources which this rule evaluates. See `Evaluating Additional Resource Types
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_,
            and
            `Supported AWS Resource Types <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources>`_.
        :type ResourceType: str
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        """
        super(NonCompliantEvaluation, self).__init__(
            AWSConfigEvaluation.TYPE_NON_COMPLIANT,
            Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )


class NotApplicableEvaluation(AWSConfigEvaluation):
    """
    This resource is not applicable for this rule.
    """

    def __init__(self, ResourceType, ResourceId=None,
                 OrderingTimestamp=None):
        """

        :param ResourceType:  A list of AWS resources which this rule evaluates. See `Evaluating Additional Resource Types
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_,
            and
            `Supported AWS Resource Types <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources>`_.
        :type ResourceType: str
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        """
        super(NotApplicableEvaluation, self).__init__(
            AWSConfigEvaluation.TYPE_NOT_APPLICABLE,
            "The rule doesn't apply to resources of type " + ResourceType + ".",
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )


class InsufficientDataEvaluation(AWSConfigEvaluation):
    """
    AWS Config returns the INSUFFICIENT_DATA value when no evaluation results are available for the AWS resource or
    Config rule.
    """

    def __init__(self, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        """

        :param Annotation: An explanation to attach to the evaluation result. Shown in the AWS Config Console.
        :type Annotation: str
        :param ResourceType:  A list of AWS resources which this rule evaluates. See `Evaluating Additional Resource Types
            <http://docs.aws.amazon.com/config/latest/developerguide/evaluate-config_develop-rules_nodejs.html#creating-custom-rules-for-additional-resource-types>`_,
            and
            `Supported AWS Resource Types <http://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources>`_.
        :type ResourceType: str
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :type ResourceId: str
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        """
        super(InsufficientDataEvaluation, self).__init__(
            AWSConfigEvaluation.TYPE_INSUFFICIENT_DATA,
            Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )
