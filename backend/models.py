from sqlalchemy import Column, Integer, String, Float, Date
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(Float)
    type = Column(String)  # 'income' or 'expense'
    category = Column(String, index=True)
    date = Column(Date)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    limit_amount = Column(Float)

class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="ahurtado0129")
    password = Column(String, nullable=True)
