from mqtt import mqtt
from db import db
import threading

# on_message is called from mqtt client
# therefore this function runs under the client thread
# and sometimes you would need a lock

lock = threading.Lock()


def on_message(client, userdata, msg):
    # -------------------------------------------------
    # doing something with message
    # -------------------------------------------------
    print("INCOMING Message: ", msg.topic, msg.payload)
    id = msg.payload.decode("utf-8")
    result = db.query(sql="SELECT name FROM makerspace.user WHERE rfid=%s", param=(id,))
    if result == tuple():
        print("No data for this id: " + id)
    else:
        print(result)


mqtt.on_message = on_message
