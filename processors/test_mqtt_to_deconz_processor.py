#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json
import logging
import sys
from string import Template

from . mqtt_to_deconz_processor import MqttToDeconzProcessor

logger = logging.getLogger(__name__)

class TestMqtt(object):
    
    def __init__(self):
        self.subscriptions = []
        self.topic = None
        self.msg = None
        self.has_published = None
    
    def subscribe_to(self, topic, clbk):
        self.subscriptions.append(topic)
    
    def get_has_subscription_to(self, topic):
        if topic in self.subscriptions:
            return True
        else:
            return False
        
class TestDeconzWS(object):
    def __init__(self):
        self.received = {}
        self.msg = None
        
    def reinit(self):
        self.received = {}
        self.msg = None
            
    def send(self, path, value):
        self.received[path] = value
        
    def get_has_received(self):
        return True if len(self.received) > 0 else False
        
    def get_for_path(self, path):
        return self.received.get(path, None)

class TestMqttToDeconzProcessor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("logger configured")

    def check_with_type(self, value_received, extract_type="jsonpath", extract_expression="", output_expression="", transform_expression=""):
        
        st = '''
        [
            {
                "type": "mqtt->deconz",
                "description": "Check 1",
                "extract-type": "${typ}",
                "extract-expression": "${extract}",
                "transform-expression": "${transform}",
                "output-expression": "${output}",
                "source-mqtt-topic": "test/Test",
                "target-path": "/bla/state"
            }
        ]
        '''
        t = Template(st)
        final_message = t.substitute(typ=extract_type, extract=extract_expression, output=output_expression, transform=transform_expression)
        
        rules = json.loads(final_message)
        test_mqtt = TestMqtt()
        test_deconz = TestDeconzWS()
        
        testee = MqttToDeconzProcessor(rules, test_mqtt, test_deconz)
       
        testee.process_message("test/Test", None, value_received)
        res = test_deconz.get_for_path("/bla/state")
 
        return res
        
    def check_without_extract(self, value_received, output_expression="", transform_expression=""):
        
        st = '''
        [
            {
                "type": "mqtt->deconz",
                "description": "Check 1",
                "transform-expression": "${transform}",
                "output-expression": "${output}",
                "source-mqtt-topic": "test/Test",
                "target-path": "/bla/state"
            }
        ]
        '''
        t = Template(st)
        final_message = t.substitute(output=output_expression, transform=transform_expression)
        
        rules = json.loads(final_message)
        test_mqtt = TestMqtt()
        test_deconz = TestDeconzWS()
        
        testee = MqttToDeconzProcessor(rules, test_mqtt, test_deconz)
       
        testee.process_message("test/Test", None, value_received)
        res = test_deconz.get_for_path("/bla/state")
 
        return res

    def test_transforms(self):
        
        # float transform
        transform_expression = "float"
        output_expression = "{:.2f}"
        value_received = "8"
        res1 = self.check_without_extract(value_received, output_expression=output_expression, transform_expression=transform_expression)
        self.assertEqual(res1, "8.00")
        
        # divide by 100 transform
        transform_expression = "divide-by-100"
        output_expression = "{:.2f}"
        value_received = "1234.56"
        res1 = self.check_without_extract(value_received, output_expression=output_expression, transform_expression=transform_expression)
        self.assertEqual(res1, "12.35")
        
    def test_single_numbers(self):
        
        extract_expression = "[0-9.?0-9*]+"
        output_expression = "{{ \\\"set_to\\\": {0} }}"
        value_received = "8"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"set_to\": 8 }")
        
        value_received = "42"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"set_to\": 42 }")
        
        value_received = "42.3"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"set_to\": 42.3 }")
        
        value_received = "42 666"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"set_to\": 42 }")
        
        # without output_expression
        value_received = "42"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression)
        self.assertEqual(res1, "42")
        
    def test_single_strings(self):
        extract_expression = "[0-9a-zA-Z]+"
        output_expression = "{{ \\\"name\\\": \\\"{0}\\\" }}"
        
        value_received = "Hello"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"name\": \"Hello\" }")
        
        value_received = "Hi There"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"name\": \"Hi\" }")
        
        # without output_expression
        value_received = "foo"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression)
        self.assertEqual(res1, "foo")
        
    def test_multiple_number_matches(self):
        extract_expression = "[0-9]+"
        output_expression = "{{ \\\"first\\\": {0}, \\\"second\\\": {1} }}"
        value_received = "0815 42"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"first\": 0815, \"second\": 42 }")
        
        # without output_expression
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression)
        assert res1 == ["0815", "42"]
        
    def test_multiple_string_matches(self):
        extract_expression = "[a-zA-Z]+"
        output_expression = "{{ \\\"first\\\": \\\"{0}\\\", \\\"second\\\": \\\"{1}\\\" }}"
        value_received = "foo bar"
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"first\": \"foo\", \"second\": \"bar\" }")
        
        # without output_expression
        res1 = self.check_with_type(value_received, extract_type="regex_multi", extract_expression=extract_expression)
        assert res1 == ["foo", "bar"]

    def test_single_bools(self):
        extract_expression = "[Oo][Nn]|[Tt][Rr][Uu][Ee]|1"
        output_expression = "{{ \\\"success\\\": {} }}"
        value_received = "True"
        res1 = self.check_with_type(value_received, extract_type="regex", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"success\": true }")
        
        value_received = "false"
        res1 = self.check_with_type(value_received, extract_type="regex", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"success\": false }")

        value_received = "something_that_is_not_true"
        res1 = self.check_with_type(value_received, extract_type="regex", extract_expression=extract_expression, output_expression=output_expression)
        self.assertEqual(res1, "{ \"success\": false }")
        
        # without output_expression
        value_received = "foo"
        res1 = self.check_with_type(value_received, extract_type="regex", extract_expression=extract_expression)
        self.assertEqual(res1, "false")
        
        value_received = "ON"
        res1 = self.check_with_type(value_received, extract_type="regex", extract_expression=extract_expression)
        self.assertEqual(res1, "true")
        

    def test_regex(self):
        import re
        
        patt = "[Oo][Nn]|[Tt][Rr][Uu][Ee]|1"
        p = re.compile(patt)
        
        self.assertTrue(p.match("True"))
        self.assertTrue(p.match("true"))
        self.assertTrue(p.match("TrUe"))
        
        self.assertTrue(p.match("on"))
        self.assertTrue(p.match("On"))
        
        self.assertTrue(p.match("1"))
        
        
        self.assertFalse(p.match("false"))
        self.assertFalse(p.match("tru"))
        
        self.assertFalse(p.match("0"))
