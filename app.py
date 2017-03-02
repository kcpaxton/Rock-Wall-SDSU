from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from databaseDefinition import *
import datetime
from sqlalchemy import text
import sqlalchemy

engine = create_engine('sqlite:///RockWallDatabase.db', echo=True)
 
app = Flask(__name__)
 
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/')
def home():
    logMessage('Begin home')
    if session.get('isLoggedIn'):
        return "Hello Boss!  <a href='/logout'>Logout</a>"
    else:
        return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
    logMessage('Begin login')

    userAccount = UserAccount(str(request.form['email']), str(request.form['password']), "")
    
    if checkLoginSucess(userAccount): 
        session['isLoggedIn'] = True
    else:
        error = 'Invalid credentials!'
        return render_template('login.html', error = error)

    return render_template('index.html')
 
@app.route('/logout')
def logout():
    logMessage('Begin logout')
    session['isLoggedIn'] = False
    return home()

@app.route('/createAccount')
def createAccount():
    logMessage('Begin createAccount')
    return render_template('createAccount.html')  

@app.route('/createAccountRoute', methods=['POST'])
def createAccountRoute(): 
    logMessage('Begin createAccountRoute')

    userAccount = UserAccount(str(request.form['email']), str(request.form['password']), str(request.form['accountType']))
    logMessage("here")
    postConfirmPassword = str(request.form['confirmPassword'])
    logMessage(userAccount.email + userAccount.password + postConfirmPassword + userAccount.accountType)

    isCreateAccountSuccess = True
    error = None

    if checkEmailExists(userAccount):
        error = 'Email already exists!'
        isCreateAccountSuccess = False

    elif userAccount.password != postConfirmPassword:
        error = 'Password do not match!'
        isCreateAccountSuccess = False

    if isCreateAccountSuccess == False: 
        return render_template('createAccount.html', error = error)


    # Global sessions to be used in authetnicateCreateAccount (don't know how to JSON)
    session['newAccountEmail'] = userAccount.email
    session['newAccountPassword'] = userAccount.password 
    newAccountType = userAccount.accountType
    session['newAccountType'] = userAccount.accountType
   
    return render_template('authenticateCreateAccount.html', accountType = session.get('newAccountType'))
    

@app.route('/authenticateCreateAccount', methods=['POST'])
def authenticateCreateAccount():
    logMessage("Begin authenticateCreateAccount")
    userAccount = UserAccount(str(request.form['email']), str(request.form['password']), findAccountType(request.form['email']))
    newUser = UserAccount(session.get('newAccountEmail'), session.get('newAccountPassword'), session.get('newAccountType'))
    
    if checkLoginSucess(userAccount):
        addUser(newUser) 
    else:
        error = 'Invalid credentials!'
        return render_template('authenticateCreateAccount.html', error = error, accountType = userAccount.accountType)

    session['isLoggedIn'] = False
    return home()


@app.route('/changePassword')
def changePassword():
    logMessage('Begin changePassword')
    return render_template('changePassword.html')  

@app.route('/changePasswordRoute', methods=['POST'])
def changePasswordRoute():
    logMessage('Begin changePasswordRoute')

    accountType = findAccountType(str(request.form['email']))

    userAccount = UserAccount(str(request.form['email']), str(request.form['newPassword']), accountType)
    logMessage(userAccount.email + userAccount.password + userAccount.accountType)
    postConfirmNewPassword = str(request.form['confirmNewPassword'])
    logMessage(userAccount.email + userAccount.password + postConfirmNewPassword + userAccount.accountType)
    isChangePasswordSuccess = True
    error = None
    logMessage('before if not')
    if not checkEmailExists(userAccount):
        error = 'Email does not exist!'
        isChangePasswordSuccess = False

    
    elif userAccount.password != postConfirmNewPassword:
        logMessage('before elif')
        error = 'Password do not match!'
        isChangePasswordSuccess = False

    
    if isChangePasswordSuccess == False: 
        logMessage('before if')
        return render_template('changePassword.html', error = error)

    session['changePasswordEmail'] = userAccount.email
    session['changePasswordNewPassword'] = userAccount.password
    session['changePasswordAccountType'] = findAccountType(userAccount)

    return render_template('authenticateChangePassword.html', accountType = session.get('changePasswordAccountType')) 

@app.route('/authenticateChangePassword', methods=['POST'])
def authenticateChangePassword():
    logMessage("Begin authenticateChangePassword")
    userAccount = UserAccount(str(request.form['email']), str(request.form['password']), findAccountType(request.form['email']))
    newAccount = UserAccount(session['changePasswordEmail'], session['changePasswordNewPassword'], session['changePasswordAccountType'])

    if checkLoginSucess(userAccount):
        changePassword(newAccount)
    else:
        error = 'Invalid credentials!'
        return render_template('authenticateChangePassword.html', error = error, accountType = session.get('changePasswordAccountType'))

    session['isLoggedIn'] = False
    return home()

@app.route('/employeeMenu')
def employeeMenu():
    return render_template('employeeMenu.html')



def logMessage(log):
    with open("debugLog.txt", "a") as logFile:
        print('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')
        logFile.write('{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()) + ': ' + str(log) + '\n')
    
def checkEmailExists(userAccount):
    logMessage('Begin checkEmailExists') 
    databaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = databaseSessionMaker()
    query = databaseSession.query(User).filter(User.email.in_([userAccount.email]))
    queryResult = query.first()

    return queryResult

def checkLoginSucess(userAccount):
    logMessage('Begin checkLoginSucess')    
    databaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = databaseSessionMaker()
    query = databaseSession.query(User).filter(User.email.in_([userAccount.email]), User.password.in_([userAccount.password]))
    queryResult = query.first()

    return queryResult

def addUser(userAccount):
    logMessage('Begin addUser')       
    databaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = databaseSessionMaker()
 
    user = User(userAccount.email, userAccount.password, userAccount.accountType)

    databaseSession.add(user)
    databaseSession.commit()

def deleteUser(userAccount):
    logMessage('Begin deleteUser')       

    databaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = databaseSessionMaker()
    user = databaseSession.query(User).filter(User.email.in_([userAccount.email])).one()
    databaseSession.delete(user)
    databaseSession.commit()

def changePassword(userAccount):
    logMessage('Begin changePassword')       
    deleteUser(userAccount)
    addUser(userAccount)




def findAccountType(passEmail):
    logMessage('Begin findAccountType')   

    databaseSessionMaker = sessionmaker(bind=engine)
    databaseSession = databaseSessionMaker()
    query = databaseSession.query(User.accountType).filter(User.email.in_([passEmail]))

    returnAccountType = 'null'
    for email, accountType in databaseSession.query(User.email, User.accountType):
        returnAccountType = accountType

    return returnAccountType

    # databaseSession = databaseSessionMaker()
   # query = databaseSession.query(User).filter(User.email == email)
   # logMessage(query.accountType)
    #return query.accountType 

class UserAccount:

    def __init__(self, email, password, accountType):
        self.email = email
        self.password = password
        self.accountType = accountType

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)