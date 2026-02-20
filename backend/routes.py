from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import os
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, date
from . import crud, models, schemas, database, auth


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

# --- Rotas de Convite (Dependentes) ---

@router.post("/invite", response_model=schemas.InviteResponse)
def generate_invite(current_user: models.User = Depends(auth.get_current_user_required)):
    try:
        # Importação local para evitar ciclo
        from . import invites
        # Verifica limite
        if not invites.check_dependent_limit(current_user.id):
            raise HTTPException(status_code=400, detail="Limite de dependentes atingido (Máx 4).")
        
        token = invites.create_invite_token(current_user.id)
        # URL do frontend (ajustar conforme necessidade, ou retornar só o token)
        base_url = os.getenv("FRONTEND_URL", "https://finanzas.ktuche.com") 
        invite_link = f"{base_url}/cadastro-dependente.html?token={token}"
        
        return {"invite_link": invite_link, "token": token}
    except Exception as e:
        print(f"Erro ao gerar convite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/register-dependent", response_model=schemas.User)
def register_dependent(data: schemas.DependentRegister, db: Session = Depends(get_db)):
    from . import invites
    # Validar Token
    parent_id = invites.verify_invite_token(data.token)
    if not parent_id:
        raise HTTPException(status_code=400, detail="Convite inválido ou expirado.")
        
    # Validar Limite novamente (segurança extra)
    if not invites.check_dependent_limit(parent_id):
        raise HTTPException(status_code=400, detail="Limite de dependentes atingido.")

    # Verificar se usuário já existe
    db_user = crud.get_user_by_username(db, username=data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username já cadastrado.")
    
    # Criar Dependente
    user_in = schemas.UserCreate(
        username=data.username,
        email=data.email,
        password=data.password,
        role="user",
        parent_id=parent_id
    )
    password_hash = auth.get_password_hash(data.password)
    return crud.create_user(db=db, user=user_in, password_hash=password_hash)

# --- Fim Rotas Convite ---




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


@router.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Registrar novo usuário"""
    # Verificar se usuário já existe
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Nome de usuário já existe"
        )
    
    # Criar usuário
    password_hash = auth.get_password_hash(user.password)
    return crud.create_user(db=db, user=user, password_hash=password_hash)


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

@router.get("/users/dependents", response_model=List[schemas.UserSimple])
def read_dependents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Listar dependentes do usuário logado"""
    return crud.get_dependents(db, current_user.id)


# ============ TRANSACTIONS ============

@router.post("/transactions/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)

@router.get("/transactions/", response_model=List[schemas.Transaction])
def read_transactions(
    skip: int = 0, 
    limit: int = 100,
    # Filtros opcionais
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    tipo: Optional[str] = None,
    categoria: Optional[str] = None,
    valor_min: Optional[float] = None,
    valor_max: Optional[float] = None,
    busca: Optional[str] = None,
    ordenar_por: str = "date",
    ordem: str = "desc",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Listar transações com filtros opcionais"""
    # Se houver filtros, usar busca avançada
    if any([data_inicio, data_fim, tipo, categoria, valor_min is not None, 
            valor_max is not None, busca, ordenar_por != "date", ordem != "desc"]):
        filtros = schemas.TransactionFilter(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo,
            categoria=categoria,
            valor_min=valor_min,
            valor_max=valor_max,
            busca=busca,
            ordenar_por=ordenar_por,
            ordem=ordem,
            skip=skip,
            limit=limit
        )
        transacoes, _ = crud.get_transactions_filtered(db, filtros, user_id=current_user.id)
        return transacoes
    else:
        # Busca simples original
        return crud.get_transactions(db, user_id=current_user.id, skip=skip, limit=limit)

@router.put("/transactions/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
    transaction_id: int, 
    transaction: schemas.TransactionUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem editar transações")
        
    db_transaction = crud.update_transaction(db, transaction_id, transaction, user_id=current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem excluir transações")
        
    crud.delete_transaction(db, transaction_id, user_id=current_user.id)
    return {"ok": True}


# ============ TRANSACTION SEARCH & REPORTS ============

@router.post("/transactions/search", response_model=schemas.TransactionSearchResponse)
def search_transactions(
    filtros: schemas.TransactionFilter, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Busca avançada de transações com estatísticas"""
    import math
    
    # Buscar transações filtradas
    transacoes, total = crud.get_transactions_filtered(db, filtros, user_id=current_user.id)
    
    # Calcular estatísticas
    estatisticas = crud.get_transactions_stats(db, transacoes)
    
    # Calcular paginação
    total_paginas = math.ceil(total / filtros.limit) if filtros.limit > 0 else 1
    pagina_atual = (filtros.skip // filtros.limit) + 1 if filtros.limit > 0 else 1
    
    return schemas.TransactionSearchResponse(
        transacoes=transacoes,
        total=total,
        pagina_atual=pagina_atual,
        total_paginas=total_paginas,
        estatisticas=estatisticas
    )


@router.get("/transactions/report", response_model=schemas.TransactionReport)
def get_transactions_report(
    data_inicio: date,
    data_fim: date,
    agrupar_por: str = "month",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Gerar relatório de transações com análise temporal"""
    # Obter transações e evolução temporal
    transacoes, evolucao_temporal = crud.get_transactions_by_period(
        db, data_inicio, data_fim, user_id=current_user.id, agrupar_por=agrupar_por
    )
    
    # Calcular estatísticas gerais
    estatisticas = crud.get_transactions_stats(db, transacoes)
    
    # Top categorias de despesas
    despesas = [t for t in transacoes if t.type == 'expense']
    categorias_despesas = {}
    for t in despesas:
        if t.category not in categorias_despesas:
            categorias_despesas[t.category] = {'categoria': t.category, 'total': 0, 'quantidade': 0}
        categorias_despesas[t.category]['total'] += t.amount
        categorias_despesas[t.category]['quantidade'] += 1
    
    top_categorias_despesas = sorted(
        categorias_despesas.values(), 
        key=lambda x: x['total'], 
        reverse=True
    )[:5]
    
    # Top categorias de receitas
    receitas = [t for t in transacoes if t.type == 'income']
    categorias_receitas = {}
    for t in receitas:
        if t.category not in categorias_receitas:
            categorias_receitas[t.category] = {'categoria': t.category, 'total': 0, 'quantidade': 0}
        categorias_receitas[t.category]['total'] += t.amount
        categorias_receitas[t.category]['quantidade'] += 1
    
    top_categorias_receitas = sorted(
        categorias_receitas.values(), 
        key=lambda x: x['total'], 
        reverse=True
    )[:5]
    
    return schemas.TransactionReport(
        data_inicio=data_inicio,
        data_fim=data_fim,
        transacoes=transacoes,
        estatisticas=estatisticas,
        evolucao_temporal=evolucao_temporal,
        top_categorias_despesas=top_categorias_despesas,
        top_categorias_receitas=top_categorias_receitas
    )


# ============ BUDGETS ============

@router.post("/budgets/", response_model=schemas.Budget)
def create_budget(
    budget: schemas.BudgetCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem criar orçamentos")

    current_budgets = crud.get_budgets(db, user_id=current_user.id)
    for b in current_budgets:
        if b.category.lower() == budget.category.lower():
            raise HTTPException(status_code=400, detail="Category already has a budget. Use Update.")
    return crud.create_budget(db=db, budget=budget, user_id=current_user.id)

@router.get("/budgets/", response_model=List[schemas.Budget])
def read_budgets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    # Dependentes não gerenciam orçamentos, mas podem ser impedidos de ver ou não.
    # Por enquanto, mantemos o acesso do CRUD (que retornará vazio se não tiver parent_id tratado, 
    # mas o CRUD de budgets usa user_id direto. Dependentes não tem budgets próprios).
    return crud.get_budgets(db, user_id=current_user.id)

@router.put("/budgets/{budget_id}", response_model=schemas.Budget)
def update_budget(
    budget_id: int, 
    budget: schemas.BudgetBase, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem editar orçamentos")

    db_budget = crud.update_budget(db, budget_id, budget, user_id=current_user.id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget

@router.delete("/budgets/{budget_id}")
def delete_budget(
    budget_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem excluir orçamentos")

    crud.delete_budget(db, budget_id, user_id=current_user.id)
    return {"ok": True}


# ============ SUMMARY ============

@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    transactions = crud.get_transactions(db, user_id=current_user.id, limit=1000)
    budgets = crud.get_budgets(db, user_id=current_user.id)
    
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


# ============ CATEGORIES ============

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    return crud.get_categories(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/categories/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem criar categorias")

    try:
        return crud.create_category(db=db, category=category, user_id=current_user.id)
    except Exception as e:
         # In case of duplicate, likely IntegrityError
        raise HTTPException(status_code=400, detail="Category probably already exists")

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Dependentes não podem excluir categorias")

    crud.delete_category(db, category_id, user_id=current_user.id)
    return {"ok": True}


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

