from datetime import date
from flask import Blueprint
from flask import render_template, flash, request, session, redirect
from src.mymodel import db, Dress, DressDetail, Members
from sqlalchemy import and_
from werkzeug.exceptions import HTTPException

myapp = Blueprint("myapp", __name__,template_folder='../templates')

@myapp.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    flash("Error!!")
    return render_template("about.html")


def user_or_admin():
    if 'username' not in session:
        flash("Please login or signup to continue")
        return 'nouser'
    elif session['username']!='admin':
        return 'notadmin'
    else:
        return 'admin'


@myapp.route('/')
@myapp.route('/user', methods=['GET','POST'])
def userpage():  #login
    if request.method =='POST':
        member = Members.query.filter_by(email=request.form['email']).first()

        if member != None and member.email == request.form['email'] and member.password == request.form['password']:
            session['username'] = member.username
            return showdress()

        else:
            flash("member email or password is incorrect")
            return render_template('login.html')

    elif 'username' in session:
        return showdress()
    else:
        return render_template('login.html')

@myapp.route('/signup')
def signup():
    return render_template('signup.html')

@myapp.route('/signedup', methods=['GET','POST'])
def signedup():  #login

    if request.method =='POST':
        m = Members.query.filter(Members.email == request.form['email']).first()

        if m != None:
            flash('This email already exists. Please try another one')
            return redirect('signup')
        else:
            if request.form['password'] == request.form['confirmpassword']:
                member = Members(request.form['name'], request.form['password'], request.form['email'])
                db.session.add(member)
                db.session.commit()
                return render_template('login.html')
            else:
                flash("password and confirm password do not match")
                return redirect('signup')
    else:
        return redirect('signup')

@myapp.route('/logoff')
def logoff():
    session.pop('username',None)
    return render_template('login.html')

@myapp.route('/admin')
def adminpage():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        return render_template('adminpage.html', username=session['username'])

@myapp.route('/about')
def about():
    return render_template('about.html', username=session['username'])

@myapp.route('/changepwd', methods=['GET','POST'])
def changepwd():
    if request.method == 'POST':
        m = Members.query.filter(Members.email == request.form['email']).first()
        if request.form['password'] == request.form['confirmpassword']:
            if m != None:
                m.password = request.form['password']
                db.session.commit()
                flash("Password change successful")
            else:
                flash("Password change failed, Please try again")
        else:
            flash("password and confirm password do not match")
    return render_template('changepwd.html')

@myapp.route('/searchdress', methods=['POST'])
def searchdress():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        dresslist = Dress.query.filter(Dress.name.like('%'+request.form['search']+'%')
                                      |Dress.seller.like('%'+request.form['search']+'%'))
        return render_template('showdress.html', dresslist=dresslist, frametitle="Search Dress",
                               username=session['username'])


@myapp.route('/dress', methods=['GET','POST'])
def showdress():
    if 'username' not in session:
        return userpage()

    dresslist = db.session.query(Dress.name, Dress.seller, Dress.available).all()
    return render_template('showdress.html', dresslist=dresslist, frametitle="All Dress",
                           username=session['username'])


@myapp.route('/mydress', methods=['GET','POST'])
def showmydress():
    c = user_or_admin()
    if c == 'nouser':
        return userpage()
    else:
        member=Members.query.filter(Members.username==session['username']).first()
        dresslist = db.session.query(DressDetail).filter(DressDetail.email == member.email).all()
        #dresslist = db.engine.execute("select name from DressDetail where email='" + member.email + "';")
        return render_template('showdress.html',dresslist=dresslist, frametitle="Your Dress",
                               username=session['username'])

@myapp.route('/members', methods=['GET','POST'])
def showmembers():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')

    memberlist = db.session.query(Members.username, Members.email).all()
    return render_template('showmembers.html',memberlist=memberlist, frametitle="All Members",
                           username=session['username'])


@myapp.route('/add_dress', methods=['GET','POST'])
def add_dress():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        dress = Dress.query.filter(Dress.name==request.form['dressname']).first()
        if dress != None:
            dress.seller = request.form['seller']
            dress.available = request.form['available']
            db.session.commit()
            print("successfully updated")
        else:
            db.session.add(Dress(request.form['dressname'],request.form['seller']))
            db.session.commit()
            print("successfully added")

    return render_template('add_dress.html',username=session['username'])

@myapp.route('/return_dress', methods=['GET','POST'])
def return_dress():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        b= DressDetail.query.filter(and_(DressDetail.name == request.form['dress'],
                                       DressDetail.email == request.form['email'])).first()
        if b != None:
            ReturnDress = db.session.query(Dress).filter(Dress.name == request.form['dress']).first()
            ReturnDress.available = 'Y'
            
            DressDetail.query.filter(and_(DressDetail.name == request.form['dress'],
                                       DressDetail.email == request.form['email'])).delete()
            db.session.commit()
        else:
            flash("Dressname and member email doesn't match in Dress Detail table ")
    dresslist = db.session.query(DressDetail.name, DressDetail.email, DressDetail.issuedt).all()
    return render_template('issuedress.html', username=session['username'], dresslist=dresslist, ret=True)


@myapp.route('/issue_dress', methods=['GET','POST'])
def issue_dress():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method=='POST':
        b = Dress.query.filter(and_(Dress.name == request.form['dress'], Dress.available=='Y')).first()
        m = Members.query.filter(Members.email == request.form['email']).first()
        if b != None and m != None:
            db.engine.execute("update Dress set available='N' where name='"+request.form['dress']+"';")
            db.session.add(DressDetail(request.form['dress'],request.form['email'],date.today()))
            db.session.commit()
        else:
            flash("Dress not available or member doesn't exist")
    dresslist = db.engine.execute("select name from Dress where available='Y';")
    return render_template('issuedress.html',username=session['username'],dresslist=dresslist, ret=False)

@myapp.route('/add_member', methods=['GET','POST'])
def add_member():
    c= user_or_admin()
    if c=='nouser':
        return userpage()
    elif c=='notadmin':
        flash("Please login with admin credentials")
        return render_template('login.html')
    if request.method == 'POST':
        member = Members.query.filter(Members.email==request.form['email']).first()
        if member != None:
            member.username = request.form['name']
            member.password = request.form['password']
            db.session.commit()
            print("successfully updated")
        else:
            db.session.add(Members(request.form['name'],request.form['password'],request.form['email'] ))
            db.session.commit()
            print("successfully added")

    return render_template('addmember.html',username=session['username'])
