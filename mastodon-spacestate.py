#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import config
import datetime
from mastodon import Mastodon

def set_profile_fields(profile_open_text_value):
    profile_fields = config.profile_fields
    profile_fields.append((config.spacestate_profile_key, profile_open_text_value))
    mastodon.account_update_credentials(fields=profile_fields)
    # don't be alarmed by the method name, this is just for updating profile metadata
    print(profile_fields)

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"rc != 0??? rc={rc}")
        exit(1)
    client.subscribe(config.spacestate_topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode("UTF-8")
    cur_dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if message == config.open_string:
        set_profile_fields(config.open_profile_field.format(cur_dt_string))
    elif message == config.closed_string:
        set_profile_fields(config.closed_profile_field.format(cur_dt_string))

mastodon = Mastodon(access_token=config.access_token, api_base_url=config.homeserver)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(config.mqtt_server, config.mqtt_port)
client.loop_forever()
