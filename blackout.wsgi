#!/usr/bin/python
import os
import json

with open('/etc/blackout/config.json') as config_file:
    config = json.load(config_file)

# use virtual env not venv and this will work
activate_this = config["path"] + '/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__ = activate_this))

import sys
import logging
logging.basicConfig(stream = sys.stderr)
sys.path.insert(0, config["path"])

from app import app as application
