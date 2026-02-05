from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Transactions
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

# Budgets
@router.post("/budgets/", response_model=schemas.Budget)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_db)):
    # Check if category exists
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

# Summary
@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    transactions = crud.get_transactions(db, limit=1000)
    budgets = crud.get_budgets(db)
    
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expenses
    
    # Calculate Income Breakdown for the Income Card
    income_breakdown = {}
    for t in transactions:
        if t.type == 'income':
            income_breakdown[t.category] = income_breakdown.get(t.category, 0) + t.amount

    budget_status = []
    for budget in budgets:
        # Transactions for this category
        cat_transactions = [t for t in transactions if t.category.lower() == budget.category.lower()]
        
        # Calculate Income and Expense for this category
        cat_income = sum(t.amount for t in cat_transactions if t.type == 'income')
        cat_expense = sum(t.amount for t in cat_transactions if t.type == 'expense')
        
        # Effective Limit = Defined Limit + Income (Boost)
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
            "alert": percentage >= 80,
            "critical": percentage >= 100
        })
        
    return {
        "balance": balance,
        "income": total_income,
        "expenses": total_expenses,
        "income_breakdown": income_breakdown, # New field
        "budgets": budget_status
    }

# Profile
# Profile
@router.get("/profile", response_model=schemas.Profile)
def read_profile(db: Session = Depends(get_db)):
    profile = crud.get_profile(db)
    if not profile:
        # Create default if missing
        profile = crud.update_profile(db, "admin", "1234")
    return profile

@router.put("/profile", response_model=schemas.Profile)
def update_profile(profile: schemas.ProfileCreate, db: Session = Depends(get_db)):
    return crud.update_profile(db, profile.name, profile.password)

@router.post("/login")
def login(login_data: schemas.LoginSchema, db: Session = Depends(get_db)):
    success = crud.verify_login(db, login_data)
    if not success:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    return {"ok": True, "name": login_data.name}
