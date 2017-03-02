import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databaseDefinition import *
 
engine = create_engine('sqlite:///RockWallDatabase.db', echo=True)
 
# create a Session
databaseSessionMaker = sessionmaker(bind=engine)
session = databaseSessionMaker()
 
user = User("e@gmail.com","abc123", "employee")
session.add(user)
 
user = User("a@gmail.com","abc123", "administrator")
session.add(user)
 
user = User("m@gmail.com","abc123", "master")
session.add(user)
 
# commit the record the database
session.commit()
 
session.commit()