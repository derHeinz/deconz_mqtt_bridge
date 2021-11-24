# Transformator between MQTT and deConz #

Similar to zigbee2mqtt (https://www.zigbee2mqtt.io/) it bridges messages from zigbee to mqtt.
Unlike zigbee2mqtt it uses deConz and therefore relies on the zigbee devices supported by deConz.

deConz is a zigbee communication software, see https://www.dresden-elektronik.de/funk/software/deconz.html.

mqtt is the a widely used communication protocol for home automation, see https://en.wikipedia.org/wiki/MQTT.

## Features ##
* send messages from mqtt to deConz and vice-versa
* select specific deConz messages to send to mqtt using regex matching
* select different topics to send deConz messages to
* extract-transform-output definitions, all of which can be used to 
* extract only parts of mqtt message to send to deConz using regex
* extract only parts of deConz message to send to mqtt using regex
* transform messages after extraction
* formatting messages for output after transformation


## Why ##
If you have a homeautomation software like openhab or ioBroker with mqtt support built in. 
You can use this project to integrate zigbee connected devices (added via deConz) into this homeautomation software.

## Example rules ##

### This turn on/off a light with if you send 'true'/'false' to an mqtt topic (and turn off if you send sth. else).

It works by reading messages from the given topic, matching it against the pattern given.
If it is sth. like 'true', 'on' or '1' it would send a message like "\{ 'on': true \}" to a specified light at deConz.
```
{
    "type": "mqtt->deconz",
    "description": "MQTT to deConz switch on/off",
    "source-mqtt-topic": "MySwitch/StateCommand",
    "extract-type": "regex",
    "extract-expression": "[Oo][Nn]|[Tt][Rr][Uu][Ee]|1",
    "output-expression": "{{ 'on': {} }}",
    "target-path": "/lights/00:11:22:33:44:55:66:77-01/state"
}
```



### Send 'true'/'false' to mqtt topic if the switch is turned on/off in deConz (e.g. by deConz or by any other means).

```
{
    "type": "deconz->mqtt",
    "description": "A Switch switch directive",
    "matchers": [
        {
            "type": "has-key",
            "key": "$['state'].on"
        },
        {
            "type": "keyvalue",
            "key":	"e",
            "value": "changed"
        },
        {
            "type": "keyvalue",
            "key":	"uniqueid",
            "value": "00:11:22:33:44:55:66:77-01"
        }
    ],
    "extract-type": "jsonpath",
    "extract-expression": "$['state'].on",
    "target-mqtt-topic": "MySwitch/State"
}
```
