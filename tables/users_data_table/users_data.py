from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from utils.dbBase import Base

class Users_data(Base):
    __tablename__ = "users_data"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    weight = Column(Integer)
    height = Column(Integer)
    gender = Column(String(1))

    user = relationship("Users", back_populates="user_data")