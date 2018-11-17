from flask import Flask
from threechan.tupperware import flask_blueprint

app = Flask(__name__)

app.register_blueprint(flask_blueprint, url_prefix='/')
