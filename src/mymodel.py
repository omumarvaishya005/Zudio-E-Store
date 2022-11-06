from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class Dress(db.Model):
    __tablename__ = 'dress'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    seller = db.Column(db.String(50))
    available = db.Column(db.String(1))
    def __init__(self,name,seller):
        self.name = name
        self.seller = seller
        self.available = 'Y'

class DressDetail(db.Model):
    __tablename__ ='dress_detail'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    issuedt = db.Column(db.Date)

    def __init__(self,name,email,issuedt):
        self.name = name
        self.email = email
        self.issuedt = issuedt

class Members(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)

    def __init__(self,username,password, email):
        self.username = username
        self.password = password
        self.email = email
