# -*- coding: utf-8 -*-
import json
import uuid
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get('LOGGING_LEVEL', logging.INFO))


class SQSHandler(object):
    """
    Parent class handling the sqs_endpoint discovery.
    """

    def __init__(self, sqs_env_var_name=None):
        """
        By default, store the sqs endpoint url in `SQS_ENDPOINT_URL` environment variables.

        :param sqs_endpoint_env_var_name: Change this value to use an alternative environment variables
        """
        self.sqs_endpoint_env_var_name = 'SQS_ENDPOINT_URL' if sqs_env_var_name is None else sqs_env_var_name

    @property
    def sqs_endpoint(self):
        """
        SQS URL Endpoint. Retrieved from Environment Variables.

        :raises ValueError: If the specified environment variable holding the sqs endpoint url is not present, raise
            this exception.
        :rtype str:
        :return:
        """
        if self.sqs_endpoint_env_var_name in os.environ:
            return os.environ[self.sqs_endpoint_env_var_name]
        else:
            raise ValueError("Could not find SQS Url '{0}' in '{1}'".format(
                self.sqs_endpoint_env_var_name, "','".join(os.environ.keys())
            ))


class SQSProducer(SQSHandler):
    """
    Produce a collection of payloads
    """

    def __init__(self, sqs_env_var_name=None):
        """
        Generate a unique event id

        :param args:
        :param kwargs:
        """
        super(SQSProducer, self).__init__(sqs_env_var_name)
        self.producer_id = uuid.uuid4()

    def _queue_messages(self):
        for message_batch in self._package_messages():
            response = self._send_messages(self.sqs_endpoint, message_batch)

    def _send_messages(self, queue_url, entries):
        return boto3.client('sqs').send_message_batch(
            QueueUrl=queue_url,
            Entries=entries
        )

    def _package_messages(self):
        chunk = []
        for message in self.generate_messages():

            chunk.append(self._clean_message(message, len(chunk)))

            if len(chunk) == 10:
                yield chunk
                chunk = []
        if len(chunk):
            yield chunk

    def _clean_message(self, message, id):
        string_types = [str, basestring, unicode]
        if (type(message) is dict) and ('MessageBody' not in message.keys()) \
                or type(message) in string_types:
            message = {'MessageBody': message}

        if type(message['MessageBody']) not in string_types:
            message['MessageBody'] = json.dumps(message['MessageBody'])
        message['Id'] = id
        return message

    def generate_messages(self):
        """
        Override and `yield` a message payload.

        :return: Must be serialisable in JSON.
        """
        raise NotImplementedError('{0}.generate_message() is not implemented'.format(
            self.__class__.__name__
        ))


class SQSConsumer(SQSHandler):
    def __init__(self, sqs_env_var_name=None):
        super(SQSConsumer, self).__init__(sqs_env_var_name)
