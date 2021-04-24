#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import asyncio

from automatic_websocket_reconnect import WSClient
from mqtt_connector import MQTTConnector
from processors.deconz_to_mqtt_processor import DeconzToMqttProcessor
from processors.mqtt_to_deconz_processor import MqttToDeconzProcessor

from webservice import put_value_to

logger = logging.getLogger(__name__)

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("logger configured")

def load_config(): 
    # load configuration from config file
    with open('config.json') as data_file:    
        return json.load(data_file)
        
def store_pid_file(pidfilename):
    pid = str(os.getpid())
    f = open(pidfilename, 'w')
    f.write(pid)
    f.close()

def init_deconz_ws(config, d_to_m_proc):
    websocket_url = config['websocket_url']
    api_token = config['api_token']
    debug_file = config.get('debug_file', None)
    
    def callback_fn(data, *args, **kwargs):
        logger.debug('callback received: {}'.format(data))
        # parse json from
        json_data = json.loads(data)
        if (debug_file):
            with open(debug_file,"a+") as out_file:
                out_file.write(data)
                out_file.write("\r\n")
        d_to_m_proc.process_message(json_data)
    
    client = WSClient(url=websocket_url, callback=callback_fn)
    logger.debug("ws client created, starting now")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.listen_forever())
    
    print("will never come here")
    
    return client
    
def init_deconz_rest(config):

    class Deconz(object):          
        
        def send(self, path, value_bool):
            # construct url
            api_token = config['api_token']
            rest_url = config["rest_url"]
            full_url = rest_url + "/api/" + api_token + path
            
            # construct json
            val_str = json.dumps({
                'on': value_bool
            })
            
            put_value_to(full_url, val_str)
            
    return Deconz()
    
def init_mqtt(config):
    host = config['host']
    port = config['port']
    
    mqtt = MQTTConnector(host, port)
    mqtt.start()

    return mqtt
    
def main():
    setup_logging()
    
    config = load_config()
    logger.debug("config: {}".format(config))
    
    store_pid_file(config['pidfile'])
    
    # first start mqtt connector
    mqtt_connector = init_mqtt(config['mqtt'])
    
    # start processor to forward messages from deconz to mqtt. (uses websocket connector for deconz)
    d_to_m_proc = DeconzToMqttProcessor(config['rules'], mqtt_connector)
    
    # start processor to forward message from mqtt to deconz. (uses simple rest interface for deconz)
    m_to_d_proc = MqttToDeconzProcessor(config['rules'], mqtt_connector, init_deconz_rest(config['deconz']))
    
    # start websocket deconz (this will never return)
    init_deconz_ws(config['deconz'], d_to_m_proc)
        
if __name__ == '__main__':
    main()
    