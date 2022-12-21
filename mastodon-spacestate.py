import paho.mqtt.client as mqtt
import config
import datetime
from mastodon import Mastodon

if hasattr(config, 'update_profilepic_on_spacestate_change'):
    update_profilepic_on_spacestate_change = config.update_profilepic_on_spacestate_change
else:
    # backcompat, standaard false
    update_profilepic_on_spacestate_change = False

def set_profile_fields(profile_open_text_value, picture = None):
    profile_fields = config.profile_fields
    profile_fields.append((config.spacestate_profile_key, profile_open_text_value))
    mastodon.account_update_credentials(fields=profile_fields, avatar=picture)
    # don't be alarmed by the method name, this is just for updating profile metadata
    print(profile_fields)

def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"rc != 0??? rc={rc}")
        exit(1)
    client.subscribe(config.spacestate_topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode("UTF-8")
    print(message)
    cur_dt_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_avatar = None
    new_profile_value = None
    if message == config.open_string:
        if update_profilepic_on_spacestate_change:
            new_avatar = config.spacestate_open_profilepic
        new_profile_value = config.open_profile_field.format(cur_dt_string)
    elif message == config.closed_string:
        if update_profilepic_on_spacestate_change:
            new_avatar = config.spacestate_open_profilepic
        new_profile_value = config.closed_profile_field.format(cur_dt_string)
    
    if new_profile_value is not None:
        set_profile_fields(new_profile_value, picture=new_avatar)

mastodon = Mastodon(access_token=config.access_token, api_base_url=config.homeserver)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(config.mqtt_server, config.mqtt_port)
client.loop_forever()