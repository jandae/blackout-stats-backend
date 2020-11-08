from cache import getCached
import json
from flask import jsonify, Blueprint
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/computed', methods=['GET'])
def getData():
    data = getCached('computed')
    data["days_since"] = (datetime.now() - datetime.strptime(data['last_post'], "%B %d, %Y")).days
    return data