#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json
import logging
import sys

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
            "transform-expression": "float"
        }
        '''))
        self.assertEqual(12.0, testee.get_value("12"))
        
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
