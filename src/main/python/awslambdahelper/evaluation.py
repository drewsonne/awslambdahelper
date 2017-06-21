"""
See http://docs.aws.amazon.com/config/latest/APIReference/API_Evaluation.html#config-Type-Evaluation-ComplianceResourceType
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

    def append(self, ResourceType=None, ResourceId=None,
               OrderingTimestamp=None):

        if ResourceType is not None:
            self.ComplianceResourceType = ResourceType

        if ResourceId is not None:
            self.ComplianceResourceId = ResourceId

        if OrderingTimestamp is not None:
            self.OrderingTimestamp = OrderingTimestamp

        return self

    def to_dict(self):

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


class CompliantEvaluation(AWSConfigEvaluation):
    def __init__(self, Annotation="This resource is compliant with the rule.", ResourceType=None,
                 ResourceId=None,
                 OrderingTimestamp=None):
        super(CompliantEvaluation, self).__init__(
            'COMPLIANT',
            Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp,
        )


class NonCompliantEvaluation(AWSConfigEvaluation):
    def __init__(self, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        super(NonCompliantEvaluation, self).__init__(
            'NON_COMPLIANT', Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )


class NotApplicableEvaluation(AWSConfigEvaluation):
    def __init__(self, ResourceType, ResourceId=None,
                 OrderingTimestamp=None):
        super(NotApplicableEvaluation, self).__init__(
            'NOT_APPLICABLE',
            "The rule doesn't apply to resources of type " + ResourceType + ".",
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )


class InsufficientDataEvaluation(AWSConfigEvaluation):
    def __init__(self, Annotation, ResourceType=None, ResourceId=None,
                 OrderingTimestamp=None):
        super(InsufficientDataEvaluation, self).__init__(
            'INSUFFICIENT_DATA', Annotation,
            ResourceType=ResourceType,
            ResourceId=ResourceId,
            OrderingTimestamp=OrderingTimestamp
        )
