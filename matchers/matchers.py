import logging
import jsonpath

logger = logging.getLogger(__name__)

class Matcher(object):

    def matches(self, json_expr):
        pass
    
    
class HasKeyMatcher(Matcher):

    def __init__(self, key):
        logger.debug("New HasKeyMatcher with key {}".format(key))
        self.key = key
    
    def matches(self, json):
        result = jsonpath.jsonpath(json, self.key)
        logger.debug("matching {} against {} results in {}".format(json, self.key, result))
        
        if (result):
            return True
            
        logger.debug("finally no match found.")
        return False
        
class KeyValueMatcher(Matcher):
    
    def __init__(self, key, value):
        logger.debug("New KeyValueMatcher with key {} and value {}".format(key, value))
        self.key = key
        self.value = value
        
    def matches(self, json):
        result = jsonpath.jsonpath(json, self.key)
        logger.debug("matching {} against {} result in: {}".format(json, self.key, result))
        if not result:
            logger.debug("match aborted.")
            return False

        if not result[0]:
            logger.debug("match aborted.")
            return False
            
        if (result[0] == self.value):
            return True

        logger.debug("finally no match found.")
        return False
        
def parse_matcher(matcher_config):
    if (not 'type' in matcher_config):
        raise ValueError('no type')
    t = matcher_config['type']
    
    if t == 'has-key':
        if (not 'key' in matcher_config):
            raise ValueError('no key')
        k = matcher_config['key']
        return HasKeyMatcher(k)
        
    elif t == 'keyvalue':
        if (not 'key' in matcher_config):
            raise ValueError('no key')
        k = matcher_config['key']
        if (not 'value' in matcher_config):
            raise ValueError('no value')
        v = matcher_config['value']
        return KeyValueMatcher(k, v)
        
    logger.warn("no matcher found for config {}.".format(matcher_config))
    return None
    