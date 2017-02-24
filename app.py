from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy.orm import sessionmaker
from databaseDefinition import *
import datetime

engine = create_engine('sqlite:///RockWallDatabase.db', echo=True)
 
app = Flask(__name__)
 
@app.route('/')
def home():
    logMessage('Begin index page')

    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Time!  <a href='/logout'>Logout</ 
@app.route('/login', methods=['POST'])
def do_admin_login():
    error = None
    logMessage('Begin Login Attempt...')

    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])
    POST_ACCOUNTTYPE = str(request.form['accountType'])

    logMessage('Login Attempt: ' + POST_USERNAME + ' ' + POST_PASSWORD + ' ' + POST_ACCOUNTTYPE)
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]), User.accountType.in_([POST_ACCOUNTTYPE]))
    result = query.first()
    
    if result: 
        session['logged_in'] = True
    else:
        error = 'Invalid credentials!'
        return render_template('login.html', error=error)
    return home()
 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

@app.route("/createAccount", methods=['POST'])
def createAccount():
    logMessage('Begin accountCreation page')

    if session.get('logged_in'):
        return render_template('index.html')
    logMessage('here')
    POST_USERNAME = str(request.form['username'])
    logMessage(POST_USERNAME)
    POST_PASSWORD = str(request.form['password'])
    logMessage(POST_PASSWORD)
    POST_ACCOUNTTYPE = str(request.form['accountType'])
    logMessage('Create Account Attempt: ' + POST_USERNAME + ' ' + POST_PASSWORD + ' ' + POST_ACCOUNTTYPE)



def logMessage(log):
    with open("debugLog.txt", "a") as logFile:
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')
        logFile.write('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)