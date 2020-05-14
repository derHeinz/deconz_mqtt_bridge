#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import jsonpath
import re

from matchers.matchers import parse_matcher

logger = logging.getLogger(__name__)

class ProcessorRule(object):
    
    def __init__(self, config):
    
        # parsing
        
        # description is optional
        self.description = config.get('description', '')
        logger.debug("parsing rule with description {}".format(self.description))

        # than there are cases
        # either use 'value' or use 'value-expression' with an optional 'value-format'.
        # If use 'value-expression' optionally use 'value-expression-type'
        
        if all (k in config for k in ('value', 'value-expression')):
            raise ValueError('Invalid value configuration, "value" and "value-expression" are defined.')
            
        if all (k in config for k in ('value', 'value-format')):
            raise ValueError('Invalid value configuration, "value" and "value-format" are defined.')
            
        if 'value-expression-type' in config and 'value-expression' not in config:
            raise ValueError('Invalid value configuration, "value-expression-type" is configured but "value-expression" is not defined.')
        
        if 'value' in config:
             self.value_expression = None
             self.value_format = None
             self.value_expression_type = None
             self.value = config['value']
        else:
            self.value_expression = config['value-expression']
            self.value_expression_type = config.get('value-expression-type', None)
            self.value_format = config.get('value-format', None)
            self.value = None

        # matchers are optional        
        logger.debug("loading matchers")
        self.matchers = []
        if 'matchers' in config:
            for matcher_config in config['matchers']:
                matcher = parse_matcher(matcher_config)
                self.matchers.append(matcher)
                
        # store config for later retrival of values
        self.config = config
        
    def matches(self, message):
        for matcher in self.matchers:
            if not matcher.matches(message):
                logger.debug("single matcher doesn't match - returning quickly")
                return False
        logger.debug("all match")
        return True
        
    def get_value(self, message):
        logger.debug("calling get_value with {}".format(message))
        
        if (self.value):
            return self.value
            
        if self.value_expression_type == None or self.value_expression_type == 'jsonpath':
            logger.debug("matching jsonpath {} against message {}".format(self.value_expression, message))
            result = jsonpath.jsonpath(message, self.value_expression)
            single_string_result = str(result[0])
            
            if (self.value_format):
                return self.value_format.format(single_string_result)
            
            return single_string_result
            
        elif self.value_expression_type == 'regex':
            logger.debug("matching regex {} against data {}".format(self.value_expression, message))
            
            return re.match(self.value_expression, message)

    def get_config_value(self, key):
        return self.config.get(key, '')
        
    def get_description(self):
        return self.description
        