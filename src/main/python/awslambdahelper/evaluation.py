# coding=utf-8

"""
See http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html \
#config-Type-Evaluation-ComplianceResourceType
"""
import datetime


class AWSConfigEvaluation(object):
    """
    Represents a response payload to an evaluation event
    """
    #: Define an evaluation of a resource as compliant to a rule. See `Evaluation.ComplianceType <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html#config-Type-Evaluation-ComplianceType>`_. # noqa
    TYPE_COMPLIANT = 'COMPLIANT'
    #: Define an evaluation of a resource as not being compliant to a rule. See `Evaluation.ComplianceType <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html#config-Type-Evaluation-ComplianceType>`_. # noqa
    TYPE_NON_COMPLIANT = 'NON_COMPLIANT'
    #: Define a rule as not being applicable to a specific resource. See `Evaluation.ComplianceType <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html#config-Type-Evaluation-ComplianceType>`_. # noqa
    TYPE_NOT_APPLICABLE = 'NOT_APPLICABLE'
    #: Define a rule as not having enough insufficient data for evaluate a resource. See `Evaluation.ComplianceType <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html#config-Type-Evaluation-ComplianceType>`_. # noqa
    TYPE_INSUFFICIENT_DATA = 'INSUFFICIENT_DATA'

    def __init__(self, Type, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        """

        :param Type: One of :py:attr:`~awslambdahelper.evaluation.AWSConfigEvaluation.TYPE_COMPLIANT`,
            :py:attr:`~awslambdahelper.evaluation.AWSConfigEvaluation.TYPE_NON_COMPLIANT`,
            :py:attr:`~awslambdahelper.evaluation.AWSConfigEvaluation.TYPE_NOT_APPLICABLE`, or
            :py:attr:`~awslambdahelper.evaluation.AWSConfigEvaluation.TYPE_INSUFFICIENT_DATA`.
        :param Annotation: An explanation to attach to the evaluation result. Shown in the AWS Config Console.
        :type Annotation: str
        :param ResourceType:
        :type ResourceType: str
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :type ResourceId: str
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        """
        self.OrderingTimestamp = OrderingTimestamp
        self.ComplianceResourceType = ResourceType
        self.ComplianceResourceId = ResourceId
        self.ComplianceType = Type
        self.Annotation = Annotation

    def set(self, ResourceType=None, ResourceId=None,
            OrderingTimestamp=None):
        """
        Sets variables for the evaluation, after creation.
        See the
        `Evaluation <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html>`_ resource for details.

        :param ResourceType:
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        :return: This evaluation object
        :rtype: :py:class:`~awslambdahelper.evaluation.AWSConfigEvaluation`
        """

        if ResourceType is not None:
            self.ComplianceResourceType = ResourceType

        if ResourceId is not None:
            self.ComplianceResourceId = ResourceId

        if OrderingTimestamp is not None:
            self.OrderingTimestamp = OrderingTimestamp

        return self

    def to_dict(self):
        """
        Convert the AWSConfigEvaluation object to
        an `Evaluation <http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html>`_ payload. If the
        timestamp is not set, we create one.

        :return: an AWS Config Evaluation resource
        :rtype: dict
        """

        response = {
            'ComplianceType': self.ComplianceType,
            'Annotation': self.Annotation,
            'ComplianceResourceType': self.ComplianceResourceType,
            'ComplianceResourceId': self.ComplianceResourceId
        }

        if self.OrderingTimestamp is None:
            response['OrderingTimestamp'] = datetime.datetime.utcnow().isoformat() + "Z"
        else:
            response['OrderingTimestamp'] = self.OrderingTimestamp

        return response
