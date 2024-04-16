from sqlalchemy import and_
from tables.users import Users
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
import os

class UsersService():
    def __init__(self, engine, session: Session, hasher: PasswordHasher):
        self.engine = engine
        self.session = session
        self.hasher = hasher

    def FindUser(self, username):
        try:
            return (
                self.session.query(Users)
                .filter(Users.username == username)
                .first()
            )
        except:
            return False
    
    def InsertUser(self, username, password) -> bool:
        new_user = Users(username=username, password=password)
        try:
            self.session.add(new_user)
            self.session.commit()
            return True
        except:
            self.session.rollback()
            return False
        
    def EncryptedPassword(self, password):
        return self.hasher.hash(password)
