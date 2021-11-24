#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

from . processor_rule import ProcessorRule

logger = logging.getLogger(__name__)
        
class DeconzToMqttProcessor(object):
    
    def __init__(self, rules, mqtt):
        self.processor_rules = []
        self._parse_rules(rules)
        self.mqtt = mqtt
        
    def _parse_rules(self, rules):
        self.processor_rules = []
        for rule in rules:
            logger.debug("attempting to parse {}".format(rule))
            if rule['type'] == 'deconz->mqtt':                
                pr = ProcessorRule(rule)
                self.processor_rules.append(pr)
        
    def process_message(self, msg):
        logger.debug("processing message {}".format(msg))
        for rule in self.processor_rules:
            logger.debug("processing on rule {}".format(rule.get_description()))
            if rule.matches(msg):
                topic = rule.get_config_value("target-mqtt-topic")
                message = rule.get_value(msg)
                logger.debug("rule hit! sending {} to topic {}".format(message, topic))
                try:
                    self.mqtt.publish(topic, message)
                except Exception as e:
                    logger.error(f"cannot send message, due to {e}.")
