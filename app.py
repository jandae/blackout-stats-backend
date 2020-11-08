from config import Config
import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True

from routes import main
app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")


