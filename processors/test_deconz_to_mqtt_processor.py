import unittest
import logging
import json
import sys

from . deconz_to_mqtt_processor import DeconzToMqttProcessor

class TestMqtt(object):
    
    def __init__(self):
        self.topic = None
        self.msg = None
        self.has_published = None
    
    def publish(self, topic, msg):
        self.topic = topic
        self.msg = msg
        self.has_published = True
        
    def get_topic(self):
        return self.topic
        
    def get_msg(self):
        return self.msg
        
    def get_has_published(self):
        return self.has_published
        

class TestDeconzToMqttProcessor(unittest.TestCase):

    def test_value_expression_format(self):
        # check with value-expression and value-format
        # check with value only
        rules = json.loads('''
        [
        {
            "type": "deconz->mqtt",
            "description": "Check with a static value",
            "matchers": [
                {
                    "type": "has-key",
                    "key": "$['state'].humidity"
                },{
                    "type": "keyvalue",
                    "key":	"uniqueid",
                    "value": "1234"
                }
            ],
            "value-expression": "$['state'].humidity",
            "value-format": "{0[0]}{0[1]}.{0[2]}{0[3]}",
            "mqtt-topic": "test/Test"
        }
        ]
        ''')
        
        # valid example
        test_mqtt = TestMqtt()
        testee = DeconzToMqttProcessor(rules, test_mqtt)
        testee.process_message(json.loads('{"state":{"humidity":5399},"uniqueid":"1234"}'))
        self.assertEqual("test/Test", test_mqtt.get_topic()) #topic from rules
        self.assertEqual("53.99", test_mqtt.get_msg()) # value from static value
        
    def test_static_value(self):
        # check with value only
        rules = json.loads('''
        [
        {
            "type": "deconz->mqtt",
            "description": "Check with a static value",
            "matchers": [
                {
                    "type": "keyvalue",
                    "key":	"uniqueid",
                    "value": "1234"
                }
            ],
            "value": "42",
            "mqtt-topic": "test/Test"
        }
        ]
        ''')
        
        # valid example
        test_mqtt = TestMqtt()
        testee = DeconzToMqttProcessor(rules, test_mqtt)
        testee.process_message(json.loads('{"state":{"humidity":5399},"uniqueid":"1234"}'))
        self.assertEqual("test/Test", test_mqtt.get_topic()) #topic from rules
        self.assertEqual("42", test_mqtt.get_msg()) # value from static value
        

    def test_value_expression(self):
        # check with value-expression only
        rules = json.loads('''
        [
        {
            "type": "deconz->mqtt",
            "description": "XiaomiAquara 1 Humidity",
            "matchers": [
                {
                    "type": "has-key",
                    "key": "$['state'].humidity"
                },{
                    "type": "keyvalue",
                    "key":	"e",
                    "value": "changed"
                },{
                    "type": "keyvalue",
                    "key":	"uniqueid",
                    "value": "1234"
                }
            ],
            "value-expression": "$['state'].humidity",
            "mqtt-topic": "test/XiaomiAquara1Hum"
        }
        ]
        ''')
        
        # valid example
        test_mqtt = TestMqtt()
        testee = DeconzToMqttProcessor(rules, test_mqtt)
        testee.process_message(json.loads('{"e":"changed","state":{"humidity":5399},"uniqueid":"1234"}'))
        self.assertEqual("test/XiaomiAquara1Hum", test_mqtt.get_topic()) #topic from rules
        self.assertEqual("5399", test_mqtt.get_msg()) # value from 
        
        # invalid example
        test_mqtt = TestMqtt()
        testee = DeconzToMqttProcessor(rules, test_mqtt)
        testee.process_message(json.loads('{"e":"changed","state":{"temperature":"22,7"},"uniqueid":"1234"}'))
        self.assertFalse(test_mqtt.get_has_published())