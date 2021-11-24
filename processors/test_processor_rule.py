#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json

from . deconz_to_mqtt_processor import ProcessorRule

class TestProcessorRule(unittest.TestCase):

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
