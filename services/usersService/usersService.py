from sqlalchemy import or_, and_
from tables import *
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from decimal import Decimal
import os

class UsersService():
    def __init__(self, session: Session, hasher: PasswordHasher = None):
        self.session = session
        self.hasher = hasher

    def FindUserById(self, user_id):
        try:
            return (
                self.session.query(Users, Users_data)
                .join(Users_data, Users.id == Users_data.user_id)
                .filter(Users.id == user_id)
                .first()
            )
        except:
            return False

    def FindUser(self, username_or_email):
        try:
            return (
                    self.session.query(Users)
                    .filter(or_(Users.username == username_or_email, Users.email == username_or_email))
                    .first()
                )
        except:
            return False
        
    def CheckUniqueEmailOrLogin(self, username, email):
        try:
            return (
                self.session.query(Users).filter(or_(Users.username == username, Users.email == email)).first()
            )
        except:
            return False

    
    def InsertUser(self, username, email, weight, height, gender, password) -> bool:
        try:
            new_user = Users(username=username, email=email, password=password)
            self.session.add(new_user)
            self.session.flush()

            new_user_data = Users_data(user_id=new_user.id, weight=weight, height=height, gender=gender)
            self.session.add(new_user_data)

            self.session.commit()
            return new_user.id
        except:
            self.session.rollback()
            return False
        
    def EncryptedPassword(self, password):
        return self.hasher.hash(password)
