import os
import sys
import json
import logging
import asyncio

from automatic_websocket_reconnect import WSClient
from mqtt_connector import MQTTConnector
from processors.deconz_to_mqtt_processor import DeconzToMqttProcessor

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

def init_deconz(config, clbk):
    websocket_url = config['websocket_url']
    api_token = config['api_token']
    
    client = WSClient(url=websocket_url, callback=clbk)
    logger.debug("ws client created, starting now")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.listen_forever())
    
    return client
    
def init_mqtt(config):
    host = config['host']
    port = config['port']
    
    mqtt = MQTTConnector(host, port)
    mqtt.start()

    return mqtt
    
if __name__ == '__main__':
    setup_logging()
    
    config = load_config()
    logger.debug("config: {}".format(config))
    
    store_pid_file(config['pidfile'])
    
    # first start mqtt connector
    mqtt_connector = init_mqtt(config['mqtt'])
    
    # start processor to push messages from deconz to mqtt
    d_to_m_proc = DeconzToMqttProcessor(config['rules'], mqtt_connector)
    
    def callback_fn(data, *args, **kwargs):
        # Write here your logic
        logger.debug('callback received: {}'.format(data))
        with open("results.jsons","a+") as out_file:
            out_file.write(data)
            out_file.write("\r\n")
        # parse json from
        json_data = json.loads(data)
        d_to_m_proc.process_message(json_data)
    
    # assume deconz config stuff is within config under 'deconz'
    deconz_connector = init_deconz(config['deconz'], callback_fn)
    
    