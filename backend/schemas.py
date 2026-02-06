from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class TransactionBase(BaseModel):
    description: str
    amount: float
    type: str
    category: str
    date: date

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None

class Transaction(TransactionBase):
    id: int
    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    category: str
    limit_amount: float

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    name: str

class ProfileCreate(ProfileBase):
    password: str

class LoginSchema(BaseModel):
    name: str
    password: str

class Profile(ProfileBase):
    id: int
    class Config:
        from_attributes = True


# ============ USERS ============

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ============ AUTH ============

class Token(BaseModel):
    access_token: str
    token_type: str
    user: "User"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
