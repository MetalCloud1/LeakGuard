from sqlalchemy import Column, String
from src.database import Base

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key = True, index=True)
    email = Column(String, unique = True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)