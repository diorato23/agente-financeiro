from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import os
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, date
from sqlalchemy.exc import IntegrityError
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
    if current_user.role == "subadmin":
        raise HTTPException(status_code=403, detail="Los subadministradores no pueden generar invitaciones.")
    try:
        from . import invites
        if not invites.check_dependent_limit(current_user.id):
            raise HTTPException(status_code=400, detail="Límite de dependientes alcanzado (Máx 4).")
        
        token = invites.create_invite_token(current_user.id)
        base_url = os.getenv("FRONTEND_URL", "https://finanzas.ktuche.com") 
        invite_link = f"{base_url}/cadastro-dependente.html?token={token}"
        
        return {"invite_link": invite_link, "token": token}
    except Exception as e:
        print(f"Error al generar invitación: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invite/info", response_model=schemas.InviteInfo)
def get_invite_info(token: str, db: Session = Depends(get_db)):
    from . import invites
    parent_id = invites.verify_invite_token(token)
    if not parent_id:
        raise HTTPException(status_code=400, detail="Invitación inválida o expirada.")
    
    parent = crud.get_user(db, parent_id)
    if not parent:
        raise HTTPException(status_code=404, detail="Usuario principal no encontrado.")
    
    count = invites.get_dependent_count(parent_id)
    return {
        "parent_id": parent_id,
        "parent_username": parent.username,
        "current_dependents": count,
        "max_dependents": 4
    }

@router.post("/register-dependent", response_model=schemas.User)
def register_dependent(data: schemas.DependentRegister, db: Session = Depends(get_db)):
    from . import invites
    parent_id = invites.verify_invite_token(data.token)
    if not parent_id:
        raise HTTPException(status_code=400, detail="Invitación inválida o expirada.")
        
    if not invites.check_dependent_limit(parent_id):
        raise HTTPException(status_code=400, detail="Límite de dependientes alcanzado.")

    db_user = crud.get_user_by_username(db, username=data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    
    if data.email:
        db_user_email = crud.get_user_by_email(db, email=data.email)
        if db_user_email:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    user_in = schemas.UserCreate(
        username=data.username,
        email=data.email,
        password=data.password,
        role="user",
        parent_id=parent_id
    )
    password_hash = auth.get_password_hash(data.password)
    try:
        return crud.create_user(db=db, user=user_in, password_hash=password_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Usuario o correo ya existente.")
    except Exception as e:
        print(f"Error al crear dependiente: {e}")
        raise HTTPException(status_code=500, detail="Error interno al crear el usuario. Prueba con otro nombre de usuario.")

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
    """Registrar nuevo usuario"""
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="El nombre de usuario ya existe"
        )
    
    password_hash = auth.get_password_hash(user.password)
    try:
        return crud.create_user(db=db, user=user, password_hash=password_hash)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Datos duplicados o error de integridad. Verifica usuario/correo.")
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"❌ ERROR CRÍTICO EN REGISTRO:\n{error_detail}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error interno al crear usuario. Detalle técnico: {str(e)}"
        )


@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user_required)):
    """Obtener usuario actual"""
    return current_user


@router.get("/users/dependents", response_model=List[schemas.UserSimple])
def read_dependents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Listar dependentes do usuário logado"""
    return crud.get_dependents(db, current_user.id)


# ============ USERS (Admin Only) ============

@router.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_any_admin)
):
    """Listar todos los usuarios (solo admin/subadmin)"""
    if current_user.role == "subadmin":
        # Ver apenas a si mesmo, pai e irmãos
        parent_id = current_user.parent_id or current_user.id
        from sqlalchemy import or_
        return db.query(models.User).filter(
            or_(models.User.id == parent_id, models.User.parent_id == parent_id)
        ).all()
        
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
    try:
        return crud.create_user(db=db, user=user, password_hash=password_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Usuario o correo ya existente.")
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


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
    
    try:
        return crud.update_user(db, user_id, user_update, password_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Datos duplicados o error de integridad.")
    except Exception as e:
        print(f"Error al actualizar usuario: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")


@router.patch("/users/{user_id}/toggle", response_model=schemas.User)
def toggle_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Activar/Inactivar usuario (solo admin)"""
    db_user = crud.toggle_user_status(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

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
    if current_user.parent_id and current_user.role == "user":
        raise HTTPException(status_code=403, detail="Los dependientes no pueden editar transacciones")
        
    db_transaction = crud.update_transaction(db, transaction_id, transaction, user_id=current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return db_transaction

@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id and current_user.role == "user":
        raise HTTPException(status_code=403, detail="Los dependientes no pueden eliminar transacciones")
        
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
    if current_user.parent_id and current_user.role == "user":
        raise HTTPException(status_code=403, detail="Los dependientes no pueden crear presupuestos")

    current_budgets = crud.get_budgets(db, user_id=current_user.id)
    for b in current_budgets:
        if b.category.lower() == budget.category.lower():
            raise HTTPException(status_code=400, detail="La categoría ya tiene un presupuesto. Usa Actualizar.")
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
        raise HTTPException(status_code=403, detail="Los dependientes no pueden editar presupuestos")

    db_budget = crud.update_budget(db, budget_id, budget, user_id=current_user.id)
    if db_budget is None:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    return db_budget

@router.delete("/budgets/{budget_id}")
def delete_budget(
    budget_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Los dependientes no pueden eliminar presupuestos")

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
    if current_user.parent_id and current_user.role == "user":
        raise HTTPException(status_code=403, detail="Los dependientes no pueden crear categorías")

    try:
        return crud.create_category(db=db, category=category, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="La categoría probablemente ya existe")

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    if current_user.parent_id and current_user.role == "user":
        raise HTTPException(status_code=403, detail="Los dependientes no pueden eliminar categorías")

    crud.delete_category(db, category_id, user_id=current_user.id)
    return {"ok": True}


# ============ FEATURE #17 — TRANSAÇÕES RECORRENTES ============

@router.get("/transactions/recurring/", response_model=List[schemas.Transaction])
def get_recurring_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Lista todas as transações recorrentes configuradas"""
    return crud.get_recurring_transactions(db, user_id=current_user.id)

@router.post("/transactions/apply-recurring/")
def apply_recurring_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Aplica transações recorrentes do mês atual. Idempotente — pode chamar várias vezes."""
    criadas = crud.apply_recurring_transactions(db, user_id=current_user.id)
    return {"applied": len(criadas), "transactions": [t.id for t in criadas]}

@router.delete("/transactions/recurring/{transaction_id}")
def deactivate_recurring(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Desactiva una transacción recurrente"""
    t = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id,
        models.Transaction.user_id == current_user.id,
        models.Transaction.is_recurring == True
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transacción recurrente no encontrada")
    t.recurrence_active = False
    db.commit()
    return {"ok": True}


# ============ FEATURE #6 — ALERTAS DE ORÇAMENTO ============

@router.get("/budgets/status/", response_model=List[schemas.BudgetStatus])
def get_budget_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Retorna el estado de los presupuestos con % de uso en el mes actual"""
    if current_user.parent_id:
        raise HTTPException(status_code=403, detail="Los dependientes no tienen presupuestos")
    return crud.get_budget_status(db, user_id=current_user.id)


# ============ FEATURE #3 — ANALYTICS POR CATEGORIA ============

@router.get("/analytics/categories/", response_model=schemas.CategoryAnalytics)
def get_category_analytics(
    period: str = None,  # Formato: "YYYY-MM", ex: "2026-02"
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user_required)
):
    """Retorna análise de gastos e receitas por categoria no mês especificado"""
    return crud.get_category_analytics(db, user_id=current_user.id, period=period)
