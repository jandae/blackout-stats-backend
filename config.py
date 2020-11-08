import os
import json

with open('/etc/blackout/config.json') as config_file:
    config = json.load(config_file)

class Config:
    redis_host = config["redis"]["host"]
    redis_port = config["redis"]["port"]
    redis_password = config["redis"]["password"]
    mysql_host = config["mysql"]["host"]
    mysql_user = config["mysql"]["user"]
    mysql_password = config["mysql"]["password"]
    mysql_database = config["mysql"]["database"]