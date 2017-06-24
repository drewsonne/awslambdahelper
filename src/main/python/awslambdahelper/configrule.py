# coding=utf-8
class UnimplementedMethod(Exception):
    """
    Thrown if either AWSConfigRule.find_violation_config_change() or AWSConfigRule.find_violation_scheduled() is not
    defined for the specified AWSConfigRule.call_type.
    """
    pass
