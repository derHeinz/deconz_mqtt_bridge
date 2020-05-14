#!/usr/bin/python3
# -*- coding: utf-8 -*-

import unittest
import json

from . mqtt_to_deconz_processor import MqttToDeconzProcessor


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
            
    def send(self, path, value_bool):
        self.received[path] = value_bool
        
    def get_has_received(self):
        return True if len(self.received) > 0 else False
        
    def get_for_path(self, path):
        return self.received.get(path, None)

class TestMqttToDeconzProcessor(unittest.TestCase):

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
        
    def test_value_1(self):
        rules = json.loads('''
        [
        {
            "type": "mqtt->deconz",
            "description": "Check 1",
            "value-expression-type": "regex",
            "value-expression": "[Oo][Nn]|[Tt][Rr][Uu][Ee]|1",
            "source-mqtt-topic": "test/Test",
            "target-path": "/bla/state"
        }
        ]
        ''')
    
        # valid example
        test_mqtt = TestMqtt()
        test_deconz = TestDeconzWS()
        
        testee = MqttToDeconzProcessor(rules, test_mqtt, test_deconz)
        self.assertTrue(test_mqtt.get_has_subscription_to("test/Test"))

        #1st try wrong topic
        topic = "bla"
        userdata = None
        message = "off"
        testee.process_message(topic, userdata, message)
        self.assertFalse(test_deconz.get_has_received())
        test_deconz.reinit()
        
        #2nd try (false/off/0)
        topic = "test/Test"
        userdata = None

        testee.process_message(topic, userdata, "false")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), False)
        test_deconz.reinit()
        
        testee.process_message(topic, userdata, "off")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), False)
        test_deconz.reinit()
        
        testee.process_message(topic, userdata, "0")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), False)
        test_deconz.reinit()
        
        #3rd try (true/on/1)
        topic = "test/Test"
        userdata = None
        
        testee.process_message(topic, userdata, "true")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), True)
        test_deconz.reinit()
        
        testee.process_message(topic, userdata, "on")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), True)
        test_deconz.reinit()
        
        testee.process_message(topic, userdata, "1")
        self.assertEqual(test_deconz.get_for_path("/bla/state"), True)
        test_deconz.reinit()
        
        