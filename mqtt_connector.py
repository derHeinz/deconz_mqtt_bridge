#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)

class MQTTConnector(object):
    
    def __init__(self, host, port):
        self.client = mqtt.Client()
        self.client.connect(host, port, 60)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._topic_to_callback = {}
        
    def _on_connect(self):
        logger.debug("connected to mqtt")
        
    def _on_message(self, client, userdata, message):
        logger.debug("received message {} on topic {}".format(message.payload, message.topic))
        if message.topic in self._topic_to_callback:
            clbk = self._topic_to_callback[message.topic]
            # call it
            clbk(message.topic, userdata, message.payload.decode('utf-8'))
        else:
            logger.debug("no listener to topic {}".format(message.topic))

    def start(self):
        self.client.loop_start()
        logger.debug("started loop")
        
    def publish(self, topic, msg):
        logger.debug("publishing {} to topic {}".format(msg, topic))
        self.client.publish(topic, msg)
        
    def unsubscribe_from(self, topic):
        if topic in self._topic_to_callback:
            self._topic_to_callback.pop(topic)
            logger.debug("removed topic {} subscription".format(topic))
        else:
            logger.error("there is no subscription to topic {}".format(topic))
        
    def subscribe_to(self, topic, callback, overwrite=False):
        if topic in self._topic_to_callback:
            logger.info("topic {} already registered".format(topic))
            
            if not overwrite:
                logger.info("do not re-register")
                return
            logger.info("reregister to topic {}".format(topic))
        
        if callback is None:
            logger.error("callback is invalid, do not register")
            return
        
        # register
        self._topic_to_callback[topic] = callback
        self.client.subscribe(topic)
        