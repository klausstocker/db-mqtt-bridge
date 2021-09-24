import configparser
from dictobj import DictionaryObject, MutableDictionaryObject
CONFIG_FILENAME = "db-mqtt-bridge.config"
# -----------------------------------------------------------------------------------
# read the configuration
# -----------------------------------------------------------------------------------
config = configparser.ConfigParser()
config.read(CONFIG_FILENAME)
config_mqtt = MutableDictionaryObject(config._sections["Mqtt"])
config_db = MutableDictionaryObject(config._sections["Database"])
