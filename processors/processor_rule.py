#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import jsonpath
import re
import datetime

from matchers.matchers import parse_matcher

logger = logging.getLogger(__name__)

class ProcessorRule(object):

    ERROR_INVALID_CONFIG_TEXT = "Invalid value configuration"
    
    def _raise_error_if_both(self, config, c1, c2):
        if all (k in config for k in (c1, c2)):
            self._raise_value_error(f'"{c1}" and "{c2}" are defined.')
    
    def _raise_error_if_second_missing(self, config, c1, c2):
        if c1 in config and c2 not in config:
            self._raise_value_error(f'"{c1}" is configured but "{c2}" is not defined.')
    
    def _raise_error_if_transform_expression_invalid(self):
        if not self.transform_expression:
            return
    
        valid_types = ['int', 'float']
        if self.transform_expression in  valid_types:
            return
    
        # divide-by or multiply-by
        divide_by = False
        rest = None
        if self.transform_expression.startswith(self.DIVIDE_BY_):
            divide_by = True
            rest = self.transform_expression[len(self.DIVIDE_BY_):]
        elif self.transform_expression.startswith(self.MULTIPLY_BY_):
            rest = self.transform_expression[len(self.MULTIPLY_BY_):]
        else:
            return # nothing else to validate
            
        # check whether rest of type is a number
        try:
            float(rest)
        except ValueError:
            self._raise_value_error("wrong transform_expression, multiply-by or divide-by invalid")
    
    def __init__(self, config):
    
        # parsing
        
        # description is optional
        self.description = config.get('description', '')
        logger.debug("parsing rule with description {}".format(self.description))

        # either use a static 'value', or use the 3-phase approach:
        # 
        # 3 phases: extract, transform, output
        # in each phase a -type and an -expression variable all optional. This is:
        # extract-type, extract-expression
        # transform-type, transform-expression
        # output-type, output-expression
        # 
        # supported formats (first ist default - you may specify it but if you don't the -expression is treated as if it were specified.)
        # extract-type: (jsonpath, regex, regex_multi)
        # transform-type: (typeconvert)
        # output-format: (stringformat)
        # 
        # definitions:
        # 'jsonpath': use jsonpath expression
        # 'regex': creates a json boolean 'true' if the pattern matches and 'false' otherwise
        # 'regex_multi' extract a portion of a string like number's or strings, also supports multiple extractions usign regex groups.
        # 'typeconvert' convert into a known python type (number, float, string)
        # 'stringformat' use python's string.format method to format the output
        # 
        
        self._raise_error_if_both(config, 'value', 'extract-type')
        self._raise_error_if_both(config, 'value', 'extract-expression')
        self._raise_error_if_both(config, 'value', 'transform-type')
        self._raise_error_if_both(config, 'value', 'transform-expression')
        self._raise_error_if_both(config, 'value', 'output-type')
        self._raise_error_if_both(config, 'value', 'output-expression')
        
        self._raise_error_if_second_missing(config, 'extract-type', 'extract-expression')
        self._raise_error_if_second_missing(config, 'transform-type', 'transform-expression')
        self._raise_error_if_second_missing(config, 'output-type', 'output-expression')
            
        if not config.get('extract-type', None) in [None, 'jsonpath', 'regex', 'regex_multi']:
            self._raise_value_error('"extract-type" has an invalid value.')
            
        if not config.get('transform-type', None) in [None, 'typeconvert']:
            self._raise_value_error('"transform-type" has an invalid value.')
            
        if not config.get('output-type', None) in [None, 'stringformat']:
            self._raise_value_error('"output-type" has an invalid value.')
        
        if 'value' in config:
            self.extract_type = None
            self.extract_expression = None
            self.transform_type = None
            self.transform_expression = None
            self.output_type = None
            self.output_expression = None
            
            self.value = config['value']
        else:
            self.extract_expression = config.get('extract-expression', None)
            
            extract_type_default = None
            if self.extract_expression:
                extract_type_default = 'jsonpath'
            self.extract_type = config.get('extract-type', extract_type_default)
            
            self.transform_type = config.get('transform-type', 'typeconvert')
            self.transform_expression = config.get('transform-expression', None)
            self._raise_error_if_transform_expression_invalid()
            self.output_type = config.get('output-type', 'stringformat')
            self.output_expression = config.get('output-expression', None)
        
            self.value = None
            
            if self.extract_type in ['regex', 'regex_multi']:
                # precompile regex in case it is a regex expression
                self.extract_expression_pattern = re.compile(self.extract_expression)

        # matchers are optional        
        logger.debug("loading matchers")
        self.matchers = []
        if 'matchers' in config:
            for matcher_config in config['matchers']:
                matcher = parse_matcher(matcher_config)
                self.matchers.append(matcher)
                
        # store config for later retrival of values
        self.config = config
        
    def _raise_value_error(self, msg):
        raise ValueError(", ".join([self.ERROR_INVALID_CONFIG_TEXT, self._rule_description(), msg]))
        
    def _rule_description(self):
        if self.description:
            return f"Rule with description \"{self.description}\""
        return ""
        
    def matches(self, message):
        for matcher in self.matchers:
            if not matcher.matches(message):
                logger.debug("single matcher doesn't match - returning quickly")
                return False
        logger.debug("all match")
        return True
            
    DIVIDE_BY_ = "divide-by-"
    MULTIPLY_BY_ = "multiply-by-"
    
    def _do_transform(self, extract_result):
        if not extract_result:
            return extract_result
        
        if not (self.transform_expression):
            return extract_result
            
        # do your transform
        if self.transform_expression == 'int':
            try:
                return int(extract_result)
            except ValueError:
                logger.error(f"cannot convert {extract_result} into integer")
                return extract_result
                
        if self.transform_expression == 'float':
            try:
                return float(extract_result)
            except ValueError:
                logger.error(f"cannot convert {extract_result} into float")
                return extract_result
                
        if self.transform_expression == 'localdatetime':
            try:
                extract_result_fixed = extract_result.replace('Z', '+00:00')
                datetime_utc = datetime.datetime.fromisoformat(extract_result_fixed)
                LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                return datetime_utc.astimezone(LOCAL_TIMEZONE)
            except ValueError:
                logger.error(f"cannot convert {extract_result} into datetime")
                return extract_result
                
        # divide-by or multiply-by
        divide_by = False
        rest = None
        if self.transform_expression.startswith(self.DIVIDE_BY_):
            divide_by = True
            rest = self.transform_expression[len(self.DIVIDE_BY_):]
        elif self.transform_expression.startswith(self.MULTIPLY_BY_):
            rest = self.transform_expression[len(self.MULTIPLY_BY_):]
        else:
            return extract_result
        # check whether rest of type is a number
        try:
            rest_number = float(rest)
            num = float(extract_result)
            if divide_by:
                return num/rest_number
            else:
                return num*rest_number
        except ValueError:
            logger.error(f"error converting to number or calculating with {rest}")
            return extract_result

    def _do_output(self, transform_result):
        if not transform_result:
            return transform_result
        
        if not (self.output_expression):
            return transform_result

        try:
            if isinstance(transform_result, list):
                return self.output_expression.format(*transform_result)
            return self.output_expression.format(transform_result)
        except ValueError:
            logger.error(f"cannot format {transform_result}")
            return transform_result

    def _do_extract(self, message):
        # phase 1 extract
        if self.extract_type == 'jsonpath':
            logger.debug(f"matching jsonpath {self.extract_expression} against message {message}")
            
            jsonpath_extract = jsonpath.jsonpath(message, self.extract_expression)
            return str(jsonpath_extract[0])

        elif self.extract_type == 'regex':
            logger.debug(f"matching regex {self.extract_expression} against data {message} and return bool whether matches or not")
            
            regex_res = self.extract_expression_pattern.match(message)
            return 'true' if regex_res else 'false'
            
        elif self.extract_type == 'regex_multi':
            logger.debug("matching regex {} against data {} multiple times.".format(self.extract_expression, message))
            
            extract_result = self.extract_expression_pattern.findall(message)
            # ease the use (but make it impossible in situations)
            # pro: you don't need to define the first array item if there is only one (dont' do {0[0]} but {0} or {} is enough)
            # con: in case you may get one or many results you won't be able to express anything. TODO make this deactivateable by config
            if len(extract_result) == 1:
                extract_result = extract_result[0]
            return extract_result
            
        else:
            return message

    def get_value(self, message):
        logger.debug(f"calling get_value with {message}")
        
        # if static value defined
        if (self.value):
            return self.value
            
        # 3-phases approach
        extract_result = self._do_extract(message)
        transform_result = self._do_transform(extract_result)
        output_result = self._do_output(transform_result)

        return output_result

    def get_config_value(self, key):
        return self.config.get(key, '')
        
    def get_description(self):
        return self.description
