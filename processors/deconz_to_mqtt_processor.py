import logging
import jsonpath

from matchers.matchers import parse_matcher

logger = logging.getLogger(__name__)

class ProcessorRule(object):
    
    def __init__(self, config):
    
        # parsing
        
        # description is optional
        self.description = config.get('description', '')
        logger.debug("parsing rule with description {}".format(self.description))

        # topic is mandatory
        self.topic = config['mqtt-topic']
        
        # than there are cases
        # either use 'value' or use 'value-expression' with an optional 'value-format'
        
        if all (k in config for k in ('value', 'value-expression')):
            raise ValueError('Invalid value configuration, "value" and "value-expression" are defined.')
            
        if all (k in config for k in ('value', 'value-format')):
            raise ValueError('Invalid value configuration, "value" and "value-format" are defined.')
        
        if 'value' in config:
             self.value_expression = None
             self.value_format = None
             self.value = config['value']
        else:
            self.value_expression = config['value-expression']
            self.value_format = config.get('value-format', None)
            self.value = None
        
        
        # matchers are mandatory        
        logger.debug("loading matchers")
        self.matchers = []
        for matcher_config in config['matchers']:
            matcher = parse_matcher(matcher_config)
            self.matchers.append(matcher)
        
    def matches(self, message):
        for matcher in self.matchers:
            if not matcher.matches(message):
                logger.debug("single matcher doesn't match - returning quickly")
                return False
        logger.debug("all match")
        return True
        
    def get_value(self, message):
        
        if (self.value):
            return self.value
        result = jsonpath.jsonpath(message, self.value_expression)
        single_string_result = str(result[0])
        if (self.value_format):
            return self.value_format.format(single_string_result)
        
        return single_string_result
        
    def get_topic(self):
        return self.topic
        
    def get_description(self):
        return self.description
        
        
class DeconzToMqttProcessor(object):
    
    def __init__(self, rules, mqtt):
        self.processor_rules = []
        self._parse_rules(rules)
        self.mqtt = mqtt
        
    def _parse_rules(self, rules):
        
        self.processor_rules = []
        for m in rules:
            logger.debug("attempting to parse {}".format(m))
            if m['type'] == 'deconz->mqtt':                
                pr = ProcessorRule(m)
                self.processor_rules.append(pr)
        
    def process_message(self, msg):
        logger.debug("processing message {}".format(msg))
        for rule in self.processor_rules:
            logger.debug("processing on rule {}".format(rule.get_description()))
            if rule.matches(msg):
                topic = rule.get_topic()
                message = rule.get_value(msg)
                logger.debug("rule hit! sending {} to topic {}".format(message, topic))
                self.mqtt.publish(topic, message)
        