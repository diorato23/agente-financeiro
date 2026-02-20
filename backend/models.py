from sqlalchemy import Column, Integer, String, Float, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")  # "admin" o "user"
    is_active = Column(Boolean, default=True)
    is_subscriber = Column(Boolean, default=False)  # Task 4: Bloqueio pré-assinatura
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Novos campos do Perfil
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    currency = Column(String, default="COP")  # Padrão COP
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    
    # Self-referential relationship for dependents
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    children = relationship("User", backref=backref("parent", remote_side=[id]), cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(Float)
    type = Column(String)  # 'income' or 'expense'
    category = Column(String, index=True)
    date = Column(Date)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="transactions")

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)  # Removido unique=True para permitir mesma categoria por usuário
    limit_amount = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="budgets")

class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="ahurtado0129")
    password = Column(String, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # Removido unique=True para permitir mesma categoria por usuário
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship
    user = relationship("User", back_populates="categories")
