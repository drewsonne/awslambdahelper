# -*- coding: utf-8 -*-
import string
import unittest

from awslambdahelper.producerconsumer import SQSHandler, SQSProducer


class TestConfigChangeRuleTests(unittest.TestCase):
    def test_missing_env_var(self):

        with self.assertRaises(ValueError):
            SQSHandler().sqs_endpoint

        with self.assertRaises(NotImplementedError):
            SQSProducer().generate_messages()

    def test_yield_message(self):
        class MockProducer(SQSProducer):
            def generate_messages(self):
                for m in ({},) * 12:
                    yield m

        abstract_handler = MockProducer()
        messages = list(abstract_handler._package_messages())

        self.assertListEqual(messages[0], [
            {'Id': 0, 'MessageBody': "{}"},
            {'Id': 1, 'MessageBody': "{}"},
            {'Id': 2, 'MessageBody': "{}"},
            {'Id': 3, 'MessageBody': "{}"},
            {'Id': 4, 'MessageBody': "{}"},
            {'Id': 5, 'MessageBody': "{}"},
            {'Id': 6, 'MessageBody': "{}"},
            {'Id': 7, 'MessageBody': "{}"},
            {'Id': 8, 'MessageBody': "{}"},
            {'Id': 9, 'MessageBody': "{}"}
        ])
        self.assertListEqual(messages[1], [
            {'Id': 0, 'MessageBody': "{}"},
            {'Id': 1, 'MessageBody': "{}"}
        ])

    def test_custom_ids(self):
        class MockProducer(SQSProducer):
            def generate_messages(self):
                for m in string.ascii_lowercase[:5]:
                    yield {'Id': m, 'MessageBody': m}

        abstract_handler = MockProducer()
        messages = list(abstract_handler._package_messages())

        self.assertListEqual(messages[0], [
            {'Id': 0, 'MessageBody': "a"},
            {'Id': 1, 'MessageBody': "b"},
            {'Id': 2, 'MessageBody': "c"},
            {'Id': 3, 'MessageBody': "d"},
            {'Id': 4, 'MessageBody': "e"}
        ])

    def test__clean_message(self):
        abstract_handler = SQSProducer()

        result = abstract_handler._clean_message('hallo', 9)
        self.assertDictEqual(result, {'Id': 9, 'MessageBody': 'hallo'})

        result = abstract_handler._clean_message({'hallo': 'world'}, 2)
        self.assertDictEqual(result, {'Id': 2, 'MessageBody': '{"hallo": "world"}'})

    # def test__queue_messages(self):
    #     with
    #     SQSProducer()._queue_messages()
