from cache import getCached
import json
from flask import jsonify, Blueprint

main = Blueprint('main', __name__)

@main.route('/computed', methods=['GET'])
def getData():
    data = getCached('computed')
    return jsonify(data)