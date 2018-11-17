from flask import Flask
from flask_heroku import Heroku
from threechan.tupperware import flask_blueprint

app = Flask(__name__)
app.register_blueprint(flask_blueprint, url_prefix='/')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/threechan'
heroku = Heroku(app)
