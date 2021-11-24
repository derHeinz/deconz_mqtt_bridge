#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

from . processor_rule import ProcessorRule

logger = logging.getLogger(__name__)

class MqttToDeconzProcessor(object):

    def __init__(self, rules, mqtt, deconz):
        self.deconz = deconz
        self.mqtt = mqtt
        
        self.processor_rules = []
        self._parse_rules(rules)
        self._subscribe_to_mqtt()
                
    def _parse_rules(self, rules):
        self.processor_rules = []
        for rule in rules:
            logger.debug("attempting to parse {}".format(rule))
            if rule['type'] == 'mqtt->deconz':                
                pr = ProcessorRule(rule)
                self.processor_rules.append(pr)
                
    def _subscribe_to_mqtt(self):
        for rule in self.processor_rules:
            source_topic = rule.get_config_value("source-mqtt-topic")
            logger.debug("subscribing {}".format(source_topic))
            self.mqtt.subscribe_to(source_topic, self.process_message)
    
    def process_message(self, topic, userdata, message):
        for rule in self.processor_rules:
            logger.debug("processing on rule {}".format(rule.get_description()))
            # first check rule has same topic
            source_topic = rule.get_config_value("source-mqtt-topic")
            if source_topic != topic:
                logger.debug("topic not hit")
                continue
            logger.debug("hit topic")
            
            # than check matches
            if rule.matches(message):
                logger.debug("rule hit!")
                value = rule.get_value(message)
                logger.debug("value returned was {}".format(value))
                
                # make bool from value
                value_bool = False
                if value:
                    value_bool = True
                    
                self.deconz.send(rule.get_config_value("target-path"), value)
