from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from . import crud, models, schemas, database, auth

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============ AUTH ============

@router.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login y obtener token JWT"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user_required)):
    """Obtener usuario actual"""
    return current_user


# ============ USERS (Admin Only) ============

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Listar todos los usuarios (solo admin)"""
    return crud.get_users(db, skip=skip, limit=limit)


@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Crear usuario (solo admin)"""
    # Verificar username único
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username ya existe")
    # Verificar email único si se proporciona
    if user.email and crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email ya existe")
    
    password_hash = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user, password_hash=password_hash)


@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Obtener usuario por ID (solo admin)"""
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user


@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Actualizar usuario (solo admin)"""
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar username único si se cambia
    if user_update.username and user_update.username != db_user.username:
        if crud.get_user_by_username(db, user_update.username):
            raise HTTPException(status_code=400, detail="Username ya existe")
    
    # Verificar email único si se cambia
    if user_update.email and user_update.email != db_user.email:
        if crud.get_user_by_email(db, user_update.email):
            raise HTTPException(status_code=400, detail="Email ya existe")
    
    # Hash password si se proporciona
    password_hash = None
    if user_update.password:
        password_hash = auth.get_password_hash(user_update.password)
    
    return crud.update_user(db, user_id, user_update, password_hash)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Eliminar usuario (solo admin)"""
    # No permitir auto-eliminación
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    crud.delete_user(db, user_id)
    return {"ok": True}


@router.patch("/users/{user_id}/toggle", response_model=schemas.User)
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Activar/Inactivar usuario (solo admin)"""
    # No permitir auto-inactivación
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes inactivarte a ti mismo")
    
    db_user = crud.toggle_user_active(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user


# ============ TRANSACTIONS ============

@router.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)

@router.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)

@router.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(transaction_id: int, transaction: schemas.TransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = crud.update_transaction(db, transaction_id, transaction)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    crud.delete_transaction(db, transaction_id)
    return {"ok": True}


# ============ BUDGETS ============

@router.post("/budgets/", response_model=schemas.Budget)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    current_budgets = crud.get_budgets(db)
    for b in current_budgets:
        if b.category.lower() == budget.category.lower():
            raise HTTPException(status_code=400, detail="Category already has a budget. Use Update.")
    return crud.create_budget(db=db, budget=budget)

@router.get("/budgets/", response_model=List[schemas.Budget])
def read_budgets(db: Session = Depends(get_db)):
    return crud.get_budgets(db)

@router.put("/budgets/{budget_id}", response_model=schemas.Budget)
def update_budget(budget_id: int, budget: schemas.BudgetBase, db: Session = Depends(get_db)):
    db_budget = crud.update_budget(db, budget_id, budget)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    crud.delete_budget(db, budget_id)
    return {"ok": True}


# ============ SUMMARY ============

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, limit=1000)
    budgets = crud.get_budgets(db)
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses
    
    income_breakdown = {}
    for t in transactions:
        if t.type == 'income':
            income_breakdown[t.category] = income_breakdown.get(t.category, 0) + t.amount

    budget_status = []
    for budget in budgets:
        cat_transactions = [t for t in transactions if t.category.lower() == budget.category.lower()]
        cat_income = sum(t.amount for t in cat_transactions if t.type == 'income')
        cat_expense = sum(t.amount for t in cat_transactions if t.type == 'expense')
        effective_limit = budget.limit_amount + cat_income
        percentage = (cat_expense / effective_limit) * 100 if effective_limit > 0 else 0
        
        budget_status.append({
            "id": budget.id,
            "category": budget.category,
            "limit": effective_limit,
            "original_limit": budget.limit_amount,
            "income_boost": cat_income,
            "spent": cat_expense,
            "percentage": percentage,
            "alert": percentage >= 70,
            "critical": percentage >= 90
        })
        
    return {
        "balance": balance,
        "income": total_income,
        "expenses": total_expenses,
        "income_breakdown": income_breakdown,
        "budgets": budget_status
    }


# ============ PROFILE (deprecated - backward compatibility) ============

@router.get("/profile", response_model=schemas.Profile)
def read_profile(db: Session = Depends(get_db)):
    profile = crud.get_profile(db)
    if not profile:
        profile = crud.update_profile(db, "admin", "1234")
    return profile

@router.put("/profile", response_model=schemas.Profile)
def update_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    return crud.update_profile(db, profile.name, profile.password)

@router.post("/login")
def login_legacy(login_data: schemas.LoginSchema, db: Session = Depends(get_db)):
    """Login legacy (backward compatibility) - redirecciona al nuevo sistema"""
    # Intentar autenticar con el nuevo sistema de usuarios
    user = auth.authenticate_user(db, login_data.name, login_data.password)
    if user:
        access_token = auth.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        return {
            "ok": True, 
            "name": user.username,
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role
        }
    
    # Fallback al sistema viejo de profile
    success = crud.verify_login(db, login_data)
    if not success:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"ok": True, "name": login_data.name, "role": "admin"}

