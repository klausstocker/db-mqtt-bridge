from config import config_mqtt
import paho.mqtt.client
import ssl
import datetime

print(config_mqtt)


def timestamp():
    now = datetime.datetime.now()  # current date and time
    return now.strftime("%m/%d/%Y, %H:%M:%S ")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(timestamp() + "Successfully connected to mqtt-broker")
        subs = eval(config_mqtt["subscription"])
        for sub in subs:
            print(timestamp() + "Subscribed to: ", sub)
            client.subscribe(sub)
    else:
        print(timestamp() + "Bad connection")


def on_disconnect(client, userdata, rc):
    print(timestamp() + "Disconnected from mqtt-broker " + " reason# " + str(rc))


# this will be overwritten mostly
def on_message(client, userdata, msg):
    print(msg.topic, msg.payload)


mqtt = paho.mqtt.client.Client()
mqtt.username_pw_set(username=config_mqtt.username, password=config_mqtt.password)
mqtt.on_connect = on_connect
mqtt.on_disconnect = on_disconnect
mqtt.on_message = on_message

if eval(config_mqtt.tls):
    mqtt.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_NONE,
                 tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
mqtt.connect(host=config_mqtt.host, port=int(config_mqtt.port))
mqtt.loop_start()
