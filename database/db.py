from sqlalchemy import create_engine, insert, select, Column, Integer, String, ForeignKey, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os


class dbConnection:
    def __init__(self):
        load_dotenv()

    def get_engine(self):
        url = os.getenv("URL")
        engine = create_engine(url, pool_size=50, echo=False)
        return engine


Base = declarative_base()
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    username = Column(String(50), unique=True)
    password = Column(String(50))

class UsersTableOperations():
    def __init__(self, engine):
        self.engine = engine

    def FindUser(self, username, password) -> bool:
        with self.engine.connect() as connection:
            session = sessionmaker(bind=connection)()

            try:
                user = (
                    session.query(Users)
                    .filter(and_(Users.username == username, Users.password == password))
                    .first()
                )
                if user is None:
                    return False
                else:
                    return True
            except:
                session.rollback()
                return False
            finally:
                session.close()
    
    def InsertUser(self, username, password) -> bool:
        with self.engine.connect() as connection:
            session = sessionmaker(bind=connection)()

            new_user = Users(username=username, password=password)
            try:
                session.add(new_user)
                session.commit()
                return True
            except:
                session.rollback()
                return False
            finally:
                session.close()
