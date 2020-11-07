import flask
import cache

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/api/data', methods=['GET'])
def getData():
    return cache.getCached('computed:all')

app.run(host='0.0.0.0')