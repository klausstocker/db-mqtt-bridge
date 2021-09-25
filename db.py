from config import config_db
import pymysql as mariadb
import threading
import time
from datetime import datetime

print(config_db)

CONNECTION_CHECK_INTERVAL_SECONDS = 2


def timestamp():
    now = datetime.now()  # current date and time
    return now.strftime("%m/%d/%Y, %H:%M:%S ")


# Database Class
class Db:
    def __init__(self):
        self.__db = None
        self.__lock = threading.Lock()
        self.__connection_state = False
        # starting the connection manager thread
        threading.Thread(target=self.__connection_manager).start()

    def __connection_manager(self):
        # -------------------------------------------------
        # we are checking database connection continuously
        # -------------------------------------------------
        while True:
            # -------------------------------------------------------------------------------
            #                         M A R I A - DB   or   M Y S Q L
            # -------------------------------------------------------------------------------
            try:
                with self.__lock:
                    if not self.__db:
                        # First try connecting to MariaDB/MySQL Platform
                        self.__connection_state = False
                        self.__db = mariadb.connect(
                            user=config_db.user,
                            password=config_db.password,
                            host=config_db.host,  # a Tunnel must be established or running at forexsignal.at
                            port=int(config_db.port),
                            database=config_db.database,
                            connect_timeout=5,
                            charset='utf8mb4',
                            cursorclass=mariadb.cursors.DictCursor
                        )
                        self.__db.auto_reconnect = True
            except:
                pass

            try:
                with self.__lock:
                    self.__db.ping()
                if not self.__connection_state:
                    print(timestamp() + "Database connected")
                    self.__connection_state = True

            except Exception as e:
                if self.__connection_state:
                    print(timestamp() + "Database disconnected - try reconnecting...")
                    self.__connection_state = False
                else:
                    if not self.__db:
                        print(timestamp() + "Database not connected initially")
                    else:
                        print(timestamp() + e.__str__())

            time.sleep(CONNECTION_CHECK_INTERVAL_SECONDS)

    def query(self, sql=str(), param=tuple()):
        try:
            if not self.__connection_state and (sql == str() or param == tuple()):
                raise
            with self.__lock:
                cur = self.__db.cursor()
                # sql-query
                cur.execute(sql, param)
                self.__db.commit()  # we need commit() to be update fom db
                result = cur.fetchall()
                return result
        except Exception as e:
            print(timestamp() + "Database query error: " + str(e))
            return tuple()
        finally:
            pass

    def _deny(self):
        return {"access": "no"}

    def checkRfid(self, id, address):
        # -------------------------------------------------
        # database request
        # -------------------------------------------------
        result = db.query(sql='SELECT device_id, autoOff FROM devices WHERE reader = %s', param=(address,))
        # ------------------------------------------------
        # handling the reply
        # -------------------------------------------------
        if result == tuple():
            print("No device for this address: " + address)
            return self._deny()
        
        if len(result) != 1:
            print("address (%s) is not unique, check database: " % address)
            return self._deny()

        deviceId = int(result[0]['device_id'])
        autoOff = result[0]['autoOff']
        sql = """SELECT users.rfid, rights.device_id, users.user_id, users.until, userCategories.restriction 
                FROM users INNER JOIN rights ON users.user_id = rights.user_id INNER JOIN devices ON 
                rights.device_id = devices.device_id INNER JOIN userCategories ON 
                users.userCategory = userCategories.id 
                WHERE users.rfid = %s AND rights.device_id = %s AND devices.maintenance = 0"""
        
        result = db.query(sql=sql, param=(id, deviceId))
        
        if len(result) != 1:
            return self._deny()
        
        until = result[0]['until']
        if datetime.now().date() > until:
            print('rfid %s has expired' % rfid)
            return self._deny()
            
        restriction = result[0]['restriction']
        if not eval(restriction):
            print('rfid %s is not allowed at this time' % id)
            return self._deny()
 
        return {"access": "yes", "value": int(autoOff), "unit": "s"}


if __name__ == '__main__':
    db = Db()
    print(db.checkRfid('4DAB4ED3', '192.168.234.11'))
    print(db.checkRfid('D64E381A', '192.168.234.11'))
    
