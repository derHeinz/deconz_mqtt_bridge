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
            "value-transform-expression": "/bookstore"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "value-and-expression")
        
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "value-and-output",
            "value": "xpath",
            "value-output-format": "asdf"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "value-and-output")
            
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "no-expression",
            "value-transform-expression-type": "regex"
        }
        ''')
        self._assert_error_invalid_config(rule_json, "no-expression")
        
        rule_json = json.loads('''
        {
            "type": "deconz->mqtt",
            "description": "invalid-type",
            "value-transform-expression-type": "xpath",
            "value-transform-expression": "/bookstore"
        }
        ''')
        
        self._assert_error_invalid_config(rule_json, "invalid-type")
