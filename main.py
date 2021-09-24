from mqtt import mqtt
from db import db
import threading
import json

# on_message is called from mqtt client
# therefore this function runs under the client thread
# and sometimes you would need a lock

lock = threading.Lock()


def on_message(client, userdata, msg):
    try:
        # -------------------------------------------------
        # doing stuff with message
        # -------------------------------------------------
        print("INCOMING Message: ", msg.topic, msg.payload)

        # -------------------------------------------------
        # Der esp32 sendet folgenden topic, payload Inhalt
        # -------------------------------------------------
        # TOPIC                             PAYLOAD
        # mksp/request/MAC-ADRESSE          chip id
        # Ein komkretes Beispiel:
        # TOPIC                             PAYLOAD
        # mksp/request/80:7d:3a:0f:fa:65    59d71399
        # -------------------------------------------------

        # -------------------------------------------------
        # database request
        # -------------------------------------------------
        mac = msg.topic.split("/")[-1]
        irfd = msg.payload.decode("utf-8")

        # Dieser sql string ist natürlich nur ein Beispiel

        result = db.query(sql="SELECT name FROM makerspace.user WHERE mac=%s AND irfd=%s", param=(mac, irfd))

        # simulierter result
        result = {"access": "yes", "value": 5, "unit": "min"}

        # -------------------------------------------------
        # handling the reply
        # -------------------------------------------------
        if result == tuple():
            print("Rejected id: " + irfd)
            result = dict()  # empty dict
        else:
            print(result)

        # --------------------------------
        # send mqtt message
        # -------------------------------------------------

        # -------------------------------------------------
        # Ergebnis zurück an den Sender
        # -------------------------------------------------
        # TOPIC                             PAYLOAD
        # mksp/reply/MAC-ADRESSE            access-dict
        # Ein komkretes Beispiel:
        # TOPIC                             PAYLOAD
        # mksp/reply/80:7d:3a:0f:fa:65      {"access": "yes", "value": 5, "unit": "min"}
        # -------------------------------------------------
        mqtt.publish(topic="mksp/reply/" + mac, payload=json.dumps(result).encode("utf-8"), retain=False)
    except Exception as e:
        print(e.__str__())


mqtt.on_message = on_message
