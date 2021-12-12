#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json
import logging
import sys
import datetime

from . deconz_to_mqtt_processor import ProcessorRule

logger = logging.getLogger(__name__)

class TestProcessorRule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger.info("logger configured")

    def _assert_error_invalid_config(self, rule_json, desc):
        try:
            testee = ProcessorRule(rule_json)
        except ValueError as e:
            err_txt = str(e)
            self.assertTrue(err_txt.startswith(ProcessorRule.ERROR_INVALID_CONFIG_TEXT))
            self.assertTrue(desc in err_txt)

    def _assert_parsed_equals(self, result, comparison_value, frmt):
        # test by reparse with local datetime
        dt = datetime.datetime.strptime(result, frmt)
        LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        dt = dt.astimezone(LOCAL_TIMEZONE) # set the datetime into local timezone
        dt_utc = dt.astimezone(datetime.timezone.utc) # transform into utc
        dt_utc_str = dt_utc.strftime(frmt+"Z")
        
        self.assertEqual(comparison_value, dt_utc_str)

    def _construct_json_dateformat(self, frmt):
        rule_json_1 = '''
        {
            "type": "deconz->mqtt",
            "description": "datetime_test",
            "transform-expression": "localdatetime",
            "output-expression": "{:'''
        rule_json_2 = '''}"
        }
        '''
        return json.loads(rule_json_1 + frmt + rule_json_2)

    def test_datetimes(self):
    
        # format without seconds
        frmt = "%Y-%m-%dT%H:%M"
        rule_json = self._construct_json_dateformat(frmt)
        testee = ProcessorRule(rule_json)
        val = "2021-11-17T21:22Z"
        res = testee.get_value(val)
        self._assert_parsed_equals(res, val, frmt)
        
        # some invalid values
        res = testee.get_value(None)
        res = testee.get_value("")
        res = testee.get_value("invalid")

        # format with seconds
        frmt = "%Y-%m-%dT%H:%M:%S"
        rule_json = self._construct_json_dateformat(frmt)
        testee = ProcessorRule(rule_json)
        val = "2021-11-17T21:22:00Z"
        res = testee.get_value(val)
        self._assert_parsed_equals(res, val, frmt)
        
    def test_invalid_configurations(self):
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "value-and-expression",
            "value": "42",
            "transform-expression": "/bookstore"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "value-and-expression")
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "value-and-expression",
            "value": "42",
            "extract-expression": "/bookstore"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "value-and-expression")
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "value-and-expression",
            "value": "42",
            "output-expression": "/bookstore"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "value-and-expression")
        
        
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "no-expression",
            "extract-type": "regex"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "no-expression")
        
        
        
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "invalid-type",
            "extract-type": "foo"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "invalid-type")
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "invalid-type",
            "transform-type": "bar"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "invalid-type")
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "invalid-type",
            "output-type": "foobar"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "invalid-type")
        
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "invalid-multiply-by",
            "transform-expression": "multiply-by-ten"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "wrong transform_expression")

    def test_transform_types(self):
        
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": ""
        }
        '''))
        self.assertEqual("12", testee.get_value("12"))
        
        # check int type
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "int"
        }
        '''))
        self.assertEqual(12, testee.get_value("12"))
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "int"
        }
        '''))
        self.assertEqual("asdf", testee.get_value("asdf"))
        
        # check float type
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "float"
        }
        '''))
        self.assertEqual(12.0, testee.get_value("12"))
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "float"
        }
        '''))
        self.assertEqual("foo", testee.get_value("foo"))
        
        # multiply-by type
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "multiply-by-100"
        }
        '''))
        self.assertEqual(1200, testee.get_value("12"))
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "multiply-by-100"
        }
        '''))
        self.assertEqual("foo", testee.get_value("foo"))
        
        # divide-by type
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "divide-by-100"
        }
        '''))
        self.assertEqual(12, testee.get_value("1200"))
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "divide-by-2"
        }
        '''))
        self.assertEqual(2, testee.get_value("4"))
        testee = ProcessorRule(json.loads('''
        {
            "description": "test",
            "transform-expression": "divide-by-2"
        }
        '''))
        self.assertEqual("qwert", testee.get_value("qwert"))
