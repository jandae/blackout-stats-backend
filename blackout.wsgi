#!/usr/bin/python

# use virtual env not venv and this will work
activate_this = '/var/www/blackout-stats-backend/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/blackout-stats-backend/")

from app import app as application
