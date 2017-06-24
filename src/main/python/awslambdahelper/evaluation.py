# coding=utf-8

"""
See http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html \
#config-Type-Evaluation-ComplianceResourceType
"""
import datetime


class AWSConfigEvaluation(object):
    COMPLIANCE_TYPES = ['COMPLIANT', 'NON_COMPLIANT', 'NOT_APPLICABLE', 'INSUFFICIENT_DATA']

    def __init__(self, Type, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        self.OrderingTimestamp = OrderingTimestamp
        self.ComplianceResourceType = ResourceType
        self.ComplianceResourceId = ResourceId
        self.ComplianceType = Type
        self.Annotation = Annotation

    def set(self, ResourceType=None, ResourceId=None,
            OrderingTimestamp=None):
        """
        Sets variables for the evaluation, after creation.
        See the Evaluation resource for details http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html

        :param ResourceType: One of AWSConfigEvaluation.COMPLIANCE_TYPES
        :param ResourceId: The id (eg, id-000000) or the ARN (eg, arn:aws:iam:01234567890:eu-west-1:..) for the resource
        :param OrderingTimestamp: The time of the event in AWS Config that triggered the evaluation.
        :return:
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
        an [Evaluation](http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html) payload. If the
        timestamp is not set, we create one.
        :return:
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

