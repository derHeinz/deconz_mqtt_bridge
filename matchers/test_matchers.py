#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json

from . matchers import parse_matcher, HasKeyMatcher, KeyValueMatcher

class TestHasKeyMatcher(unittest.TestCase):

    def test_HasKeyMatcher(self):
        json_expr = json.loads('{"id":"1","state":{"lastupdated":"2020-02-28T21:26:03","temperature":2612}}')
        
        self.assertTrue(HasKeyMatcher("$['state'].temperature").matches(json_expr))
        self.assertTrue(HasKeyMatcher("$.id").matches(json_expr))
        self.assertTrue(HasKeyMatcher("$.state").matches(json_expr))
        
        self.assertFalse(HasKeyMatcher("$.id2").matches(json_expr))
        self.assertFalse(HasKeyMatcher("$sate").matches(json_expr))
        self.assertFalse(HasKeyMatcher("$['state'].updated").matches(json_expr))
        self.assertFalse(HasKeyMatcher("$['state'].updated").matches(json_expr))
        
    def test_KeyValueMatcher(self):
        json_expr = json.loads('{"id":"1","state":{"lastupdated":"2020-02-28T21:26:03","temperature":2612}}')
        
        self.assertTrue(KeyValueMatcher("$['state'].temperature", 2612).matches(json_expr))
        self.assertTrue(KeyValueMatcher("$.id", "1").matches(json_expr))
        
        self.assertFalse(KeyValueMatcher("$.id", 1).matches(json_expr))
        self.assertFalse(KeyValueMatcher("$id", "1").matches(json_expr))
        
        self.assertFalse(KeyValueMatcher("$['state'].temperature", "2612").matches(json_expr))
        self.assertFalse(KeyValueMatcher("$['state'].temperature", 2613).matches(json_expr))
        
        
    def test_parse_matcher(self):
        # test of beeing HasKeyMatcher
        json_expr = json.loads('{"type": "has-key", "key": "asdf"}')
        self.assertTrue(type(parse_matcher(json_expr) is HasKeyMatcher))
        
        json_expr = json.loads('{"key": "asdf", "description": "some random information", "type": "has-key"}')
        self.assertTrue(type(parse_matcher(json_expr) is HasKeyMatcher))
        
        json_expr = json.loads('{"type": "has-key"}')
        with self.assertRaises(ValueError):
            parse_matcher(json_expr)
            
        json_expr = json.loads('{}')
        with self.assertRaises(ValueError):
            parse_matcher(json_expr)
            
        # test of beeing KeyValueMatcher
        json_expr = json.loads('{"type": "keyvalue","key": "e","value": "changed"}')
        self.assertTrue(type(parse_matcher(json_expr) is KeyValueMatcher))
        
        json_expr = json.loads('{"key": "e", "type": "keyvalue", "value": "changed"}')
        self.assertTrue(type(parse_matcher(json_expr) is KeyValueMatcher))
        
        json_expr = json.loads('{"type": "keyvalue"}')
        with self.assertRaises(ValueError):
            parse_matcher(json_expr)
            
        json_expr = json.loads('{"type": "keyvalue", "key": "a"}')
        with self.assertRaises(ValueError):
            parse_matcher(json_expr)
            
        json_expr = json.loads('{"type": "keyvalue", "value": "a"}')
        with self.assertRaises(ValueError):
            parse_matcher(json_expr)
