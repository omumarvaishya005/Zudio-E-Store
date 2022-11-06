from flask import Flask
from src.mymodel import db
from src.myroutes import myapp

app = Flask(__name__)
app.secret_key = b'testkey'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///../library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.app_context().push()
#create database if running first time
#db.session.remove()
#db.drop_all()
db.create_all()

app.register_blueprint(myapp)

if __name__ == '__main__':
    app.run()
