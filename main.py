from mqtt import mqtt
import db as database
import threading

db = database.Db()
    
def on_message(client, userdata, msg):
    try:
        # -------------------------------------------------
        # doing stuff with message
        # -------------------------------------------------
        print("INCOMING Message: ", msg.topic, msg.payload)
        id = msg.topic.split("/")[-1]
        result = db.checkRfid(id, 'dummy_address')
        # -------------------------------------------------
        # send mqtt message
        mqtt.publish(topic="mksp/reply/" + id, payload=str(result).encode("utf-8"), retain=False)
        # -------------------------------------------------
    except Exception as e:
        print(e.__str__())

if __main__ == '__main__':
    # on_message is called from mqtt client
    # therefore this function runs under the client thread
    # and sometimes you would need a lock

    lock = threading.Lock()
    mqtt.on_message = on_message
   
