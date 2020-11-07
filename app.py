import flask
import cache

app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/data', methods=['GET'])
def getData():
    return cache.getCached('computed:all')

if __name__ == "__main__":
    app.run(host='0.0.0.0')