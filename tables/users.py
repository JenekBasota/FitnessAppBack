from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    username = Column(String(16), unique=True)
    password = Column(String(128))