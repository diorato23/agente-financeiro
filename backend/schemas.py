from pydantic import BaseModel
from typing import Optional
from datetime import date

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
