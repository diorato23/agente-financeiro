from sqlalchemy.orm import Session
from . import models, schemas

# Transactions
def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    db_trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_trans:
        for key, value in transaction.dict().items():
            setattr(db_trans, key, value)
        db.commit()
        db.refresh(db_trans)
    return db_trans

def delete_transaction(db: Session, transaction_id: int):
    val = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if val:
        db.delete(val)
        db.commit()
    return val

# Budgets
def get_budgets(db: Session):
    return db.query(models.Budget).all()

def create_budget(db: Session, budget: schemas.BudgetCreate):
    db_budget = db.query(models.Budget).filter(models.Budget.category == budget.category).first()
    if db_budget:
        # Update existing if category matches, or handle as error? 
        # Requirement says "Include, Alter, Delete". Let's assume Create is unique, Update is separate.
        # For simplicity, if exists, we return it or update limit? Let's just create.
        # Actually logic for create should probably fail if exists or just update. 
        # Let's keep separate update method.
        pass
    
    db_budget = models.Budget(**budget.dict())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget: schemas.BudgetBase):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if db_budget:
        db_budget.category = budget.category
        db_budget.limit_amount = budget.limit_amount
        db.commit()
        db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int):
    val = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if val:
        db.delete(val)
        db.commit()
    return val

# Profile
def get_profile(db: Session):
    return db.query(models.Profile).first()

def get_profile_by_name(db: Session, name: str):
    return db.query(models.Profile).filter(models.Profile.name == name).first()

def update_profile(db: Session, name: str, password: str = None):
    profile = db.query(models.Profile).first()
    if not profile:
        profile = models.Profile(name=name, password=password)
        db.add(profile)
    else:
        profile.name = name
        if password:
            profile.password = password
    db.commit()
    db.refresh(profile)
    return profile

def verify_login(db: Session, login_data: schemas.LoginSchema):
    # Check if any profile exists (Single user mode)
    # Or find by name
    profile = db.query(models.Profile).first()
    if not profile:
        return False # No user yet
    
    # Simple check: Name must match (case insensitive?) and Password match
    # For this specific user request: "puts name and password and enters"
    if profile.name.lower() == login_data.name.lower() and profile.password == login_data.password:
        return True
    return False
