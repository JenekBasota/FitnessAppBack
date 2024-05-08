from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from utils.dbBase import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    username = Column(String(16), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String(128))
    weight = Column(Integer)
    height = Column(Integer)
    gender = Column(String(1))