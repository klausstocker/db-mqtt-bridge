from config import config_db
import pymysql as mariadb
from dictobj import DictionaryObject, MutableDictionaryObject
import threading
import time
import datetime

print(config_db)

CONNECTION_CHECK_INTERVAL_SECONDS = 2


def timestamp():
    now = datetime.datetime.now()  # current date and time
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
            if sql == str() or param == tuple():
                raise
            with self.__lock:
                cur = self.__db.cursor()
                # sql-query
                cur.execute(sql, param)
                self.__db.commit()  # we need commit() to be update fom db
                result = cur.fetchall()
                return result
        except:
            print(timestamp() + "Database query error")
            return tuple()
        finally:
            pass


db = Db()
