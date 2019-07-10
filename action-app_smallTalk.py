#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import os


CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class SnipsSmallTalk(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
        #get the configuration if needed
        try:
           self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def howareyou_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        
        message = "null"
        try:
            # Read CPU temperature
            cpu_temp = os.popen("vcgencmd measure_temp").readline()
            cpu_temp = cpu_temp.replace("temp=", "")
            cpu_temp = cpu_temp.replace("'C\n", "")
            cpu_temp2 = float(cpu_temp)
        
            if cpu_temp2 < 60:
                message = "Ganz gut! Meine Plantine ist " + cpu_temp + " Grad warm"
            else:
                message = "Nicht so gut! Meine Platine ist " + cpu_temp + " Grad heiß. Kannst du da was machen?"
        
        except :
            message = "Ich weiß nicht so genau. Ich konnte meine Temperatur nicht ermitteln"
    
        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, message, "SnipsSmallTalkAPP")

    def whatdoyouthink_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        
        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, "Ich habe leider noch kein Bewusstsein", "SnipsSmallTalkAPP")

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'xion:howareyou':
            self.howareyou_callback(hermes, intent_message)
        if coming_intent == 'xion:whatdoyouthink':
            self.whatdoyouthink_callback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    SnipsSmallTalk()
