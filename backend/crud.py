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

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate):
    db_trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_trans:
        update_data = transaction.dict(exclude_unset=True)
        # Convert date string to date object if present
        if 'date' in update_data and update_data['date']:
            from datetime import datetime
            if isinstance(update_data['date'], str):
                try:
                    update_data['date'] = datetime.strptime(update_data['date'], '%Y-%m-%d').date()
                except ValueError:
                    pass # Keep as is if format is wrong (SQLAlchemy might handle or fail)

        for key, value in update_data.items():
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


# ============ CATEGORIES ============

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db.query(models.Category).filter(models.Category.id == category_id).delete()
    db.commit()


# ============ USERS ============

def get_user(db: Session, user_id: int):
    """Obtener usuario por ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Obtener usuario por username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Obtener usuario por email"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtener lista de usuarios"""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, password_hash: str):
    """Crear usuario"""
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, password_hash: str = None):
    """Actualizar usuario"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user_update.username is not None:
            db_user.username = user_update.username
        if user_update.email is not None:
            db_user.email = user_update.email
        if user_update.role is not None:
            db_user.role = user_update.role
        if user_update.is_active is not None:
            db_user.is_active = user_update.is_active
        if password_hash:
            db_user.password_hash = password_hash
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Eliminar usuario"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def toggle_user_active(db: Session, user_id: int):
    """Activar/Inactivar usuario"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_active = not db_user.is_active
        db.commit()
        db.refresh(db_user)
    return db_user
