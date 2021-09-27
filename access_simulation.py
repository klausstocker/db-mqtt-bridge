from config import config_mqtt
import paho.mqtt.client
import ssl
import datetime
import random
import time

# for info only
# print(config_mqtt)
list_of_mac = ["80:7d:3a:0f:fa:65", "81:7d:3a:0f:fa:66", "82:7d:3a:0f:fa:67"]
list_of_id = ["59d71399", "69d71398", "79d71397"]


def timestamp():
    now = datetime.datetime.now()  # current date and time
    return now.strftime("%m/%d/%Y, %H:%M:%S ")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(timestamp() + "Successfully connected to mqtt-broker")
    else:
        print(timestamp() + "Bad connection")


def on_disconnect(client, userdata, rc):
    print(timestamp() + "Disconnected from mqtt-broker " + " reason# " + str(rc))


def on_message(client, userdata, msg):
    print("RECEIVED ", msg.topic, msg.payload)


if __name__ == '__main__':
    mqtt = paho.mqtt.client.Client()
    mqtt.username_pw_set(username=config_mqtt.username, password=config_mqtt.password)
    mqtt.on_connect = on_connect
    mqtt.on_disconnect = on_disconnect
    mqtt.on_message = on_message  # this will be overwritten mostly

    if eval(config_mqtt.tls):
        mqtt.tls_set(ca_certs=None,
                     certfile=None,
                     keyfile=None,
                     cert_reqs=ssl.CERT_NONE,
                     tls_version=ssl.PROTOCOL_TLSv1_2,
                     ciphers=None)

    mqtt.connect(host=config_mqtt.host, port=int(config_mqtt.port))
    mqtt.loop_start()  # the loop also manages reconnecting
    time.sleep(2)  # wait for connect
    while True:
        try:
            # make random mac and id from list
            index = random.randint(0, len(list_of_mac)-1)
            mac = list_of_mac[index]
            index = random.randint(0, len(list_of_mac)-1)
            id = list_of_id[index]

            # generating the topic
            topic = "mksp/device/request/%mac%"
            topic = topic.replace("%mac%", mac)

            payload = id
            print("PUBLISHED ", topic, payload)
            mqtt.publish(topic, payload, retain=False)
        except:
            pass
        finally:
            time.sleep(3)
