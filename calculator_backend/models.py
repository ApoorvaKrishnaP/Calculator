from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from calculator_backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    calculations = relationship("History", back_populates="user")
class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expression = Column(String)
    result = Column(String)
    user = relationship("User", back_populates="calculations")