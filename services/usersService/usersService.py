from sqlalchemy import or_, and_
from tables import *
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from decimal import Decimal
import os

class UsersService():
    def __init__(self, session: Session, hasher: PasswordHasher):
        self.session = session
        self.hasher = hasher

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
            self.session.commit()
            new_user_data = Users_data(user_id=new_user.id, weight=Decimal(f'{weight:.2f}'), height=height, gender=gender)
            self.session.add(new_user_data)
            self.session.commit()
            return new_user.id
        except:
            self.session.rollback()
            return False
        
    def EncryptedPassword(self, password):
        return self.hasher.hash(password)
