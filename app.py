from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy.orm import sessionmaker
from databaseDefinition import *
import datetime

engine = create_engine('sqlite:///RockWallDatabase.db', echo=True)
 
app = Flask(__name__)
 
@app.route('/')
@app.route('/index')
def home():
    logMessage('Begin index page')
    if session.get('isLoggedIn'):
        return "Hello Boss!  <a href='/logout'>Logout</a>"
    else:
        return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    logMessage('Begin Login Attempt...')

    postEmail = str(request.form['email'])
    postPassword = str(request.form['password'])
    postAccountType = str(request.form['accountType'])

    logMessage('Login Attempt: ' + postEmail + ' ' + postPassword + ' ' + postAccountType)
    
    if checkLoginSucess(postEmail, postPassword, postAccountType): 
        session['isLoggedIn'] = True
    else:
        error = 'Invalid credentials!'
        return render_template('login.html', error = error)
    return render_template('index.html')
 
@app.route('/logout')
def logout():
    session['isLoggedIn'] = False
    return home()

@app.route('/createAccount')
def createAccount():
    return render_template('createAccount.html')  

@app.route('/createAccountRoute', methods=['POST'])
def createAccountRoute(): 
    logMessage('Begin Create Account Attempt...')
    postEmail = str(request.form['email'])
    postPassword = str(request.form['password'])
    postConfirmPassword = str(request.form['confirmPassword'])
    postAccountType = str(request.form['accountType'])

    logMessage('Create Account Attempt: ' + postEmail + ' ' + postPassword + ' ' + postConfirmPassword + ' ' + postAccountType)

    isCreateAccountSuccess = True
    error = None

    if checkEmailExists(postEmail):
        error = 'Email already exists!'
        isCreateAccountSuccess = False

    elif postPassword != postConfirmPassword:
        error = 'Password do not match!'
        isCreateAccountSuccess = False

    if isCreateAccountSuccess == False: 
        return render_template('createAccount.html', error = error)
   
    session['creationAccountType'] = postAccountType
    return render_template('authentication.html', accountType = postAccountType) 
    
    #return home()


@app.route('/changePassword')
def changePassword():
    return render_template('changePassword.html')  

@app.route('/authentication', methods=['POST'])
def authenticateNewUser():
    logMessage("Start authenticateNewUser")
    postEmail = str(request.form['email'])
    postPassword = str(request.form['password'])
    postAccountType = str(request.form['accountType'])

    if checkLoginSucess(postEmail, postPassword, postAccountType):
        logMessage("Create new Account here.")
    else:
        error = 'Invalid credentials!'
        return render_template('authentication.html', error = error, accountType = session.get('creationAccountType'))

    session['isLoggedIn'] = False
    return home()

def logMessage(log):
    with open("debugLog.txt", "a") as logFile:
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')
        logFile.write('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')

def checkEmailExists(postEmail):
    dataBaseSessionMaker = sessionmaker(bind=engine)
    dataBaseSession = dataBaseSessionMaker()
    query = dataBaseSession.query(User).filter(User.email.in_([postEmail]))
    queryResult = query.first()

    return queryResult

def checkLoginSucess(postEmail, postPassword, postAccountType):
    dataBaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = dataBaseSessionMaker()
    query = databaseSession.query(User).filter(User.email.in_([postEmail]), User.password.in_([postPassword]), User.accountType.in_([postAccountType]))
    queryResult = query.first()

    return queryResult

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)