#!/usr/bin/env python
import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTConnector(object):
    
    def __init__(self, host, port):
        self.client = mqtt.Client()
        self.client.connect(host, port, 60)
        self.client.on_connect = self._on_connect
        
    def _on_connect(self):
        logger.debug("connected to mqtt")
        
    def start(self):
        self.client.loop_start()
        logger.debug("started loop")
        
    def publish(self, topic, msg):
        logger.debug("publishing {} to topic {}".format(msg, topic))
        self.client.publish(topic, msg)