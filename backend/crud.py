from sqlalchemy.orm import Session
from . import models, schemas

# Transactions
def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate, user_id: int):
    db_trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id).first()
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

def delete_transaction(db: Session, transaction_id: int, user_id: int):
    val = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.user_id == user_id).first()
    if val:
        db.delete(val)
        db.commit()
    return val

# Budgets
def get_budgets(db: Session, user_id: int):
    return db.query(models.Budget).filter(models.Budget.user_id == user_id).all()

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    # Verificar se já existe budget para esta categoria e usuário
    db_budget = db.query(models.Budget).filter(
        models.Budget.category == budget.category,
        models.Budget.user_id == user_id
    ).first()
    if db_budget:
        # Já existe, não criar duplicado
        pass
    
    db_budget = models.Budget(**budget.dict(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget: schemas.BudgetBase, user_id: int):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == user_id).first()
    if db_budget:
        db_budget.category = budget.category
        db_budget.limit_amount = budget.limit_amount
        db.commit()
        db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int):
    val = db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.user_id == user_id).first()
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

def get_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Category).filter(models.Category.user_id == user_id).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(name=category.name, user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int, user_id: int):
    db.query(models.Category).filter(models.Category.id == category_id, models.Category.user_id == user_id).delete()
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


# ============ TRANSACTION SEARCH & FILTERS ============

def get_transactions_filtered(db: Session, filtros: schemas.TransactionFilter, user_id: int):
    """Buscar transações com filtros avançados"""
    from sqlalchemy import or_, and_, desc, asc
    
    query = db.query(models.Transaction).filter(models.Transaction.user_id == user_id)
    
    # Aplicar filtros
    if filtros.data_inicio:
        query = query.filter(models.Transaction.date >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(models.Transaction.date <= filtros.data_fim)
    
    if filtros.tipo:
        query = query.filter(models.Transaction.type == filtros.tipo)
    
    if filtros.categoria:
        query = query.filter(models.Transaction.category == filtros.categoria)
    
    if filtros.valor_min is not None:
        query = query.filter(models.Transaction.amount >= filtros.valor_min)
    
    if filtros.valor_max is not None:
        query = query.filter(models.Transaction.amount <= filtros.valor_max)
    
    if filtros.busca:
        # Busca textual na descrição (case-insensitive)
        query = query.filter(models.Transaction.description.ilike(f"%{filtros.busca}%"))
    
    # Ordenação
    order_column = models.Transaction.date  # padrão
    if filtros.ordenar_por == "amount":
        order_column = models.Transaction.amount
    elif filtros.ordenar_por == "category":
        order_column = models.Transaction.category
    elif filtros.ordenar_por == "description":
        order_column = models.Transaction.description
    
    if filtros.ordem == "asc":
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    
    # Paginação
    total = query.count()
    transacoes = query.offset(filtros.skip).limit(filtros.limit).all()
    
    return transacoes, total


def get_transactions_stats(db: Session, transacoes: list = None, user_id: int = None):
    """Calcular estatísticas agregadas de transações"""
    if transacoes is None:
        if user_id:
            transacoes = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
        else:
            transacoes = db.query(models.Transaction).all()
    
    if not transacoes:
        return schemas.TransactionStats(
            total_receitas=0,
            total_despesas=0,
            saldo=0,
            quantidade_transacoes=0,
            quantidade_receitas=0,
            quantidade_despesas=0,
            media_receitas=0,
            media_despesas=0,
            por_categoria={}
        )
    
    receitas = [t for t in transacoes if t.type == 'income']
    despesas = [t for t in transacoes if t.type == 'expense']
    
    total_receitas = sum(t.amount for t in receitas)
    total_despesas = sum(t.amount for t in despesas)
    
    # Estatísticas por categoria
    por_categoria = {}
    for t in transacoes:
        if t.category not in por_categoria:
            por_categoria[t.category] = {'total': 0, 'quantidade': 0}
        por_categoria[t.category]['total'] += t.amount
        por_categoria[t.category]['quantidade'] += 1
    
    return schemas.TransactionStats(
        total_receitas=total_receitas,
        total_despesas=total_despesas,
        saldo=total_receitas - total_despesas,
        quantidade_transacoes=len(transacoes),
        quantidade_receitas=len(receitas),
        quantidade_despesas=len(despesas),
        media_receitas=total_receitas / len(receitas) if receitas else 0,
        media_despesas=total_despesas / len(despesas) if despesas else 0,
        por_categoria=por_categoria
    )


def get_transactions_by_period(db: Session, data_inicio, data_fim, user_id: int, agrupar_por: str = "month"):
    """Obter transações agrupadas por período"""
    from datetime import datetime
    from collections import defaultdict
    
    transacoes = db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.date >= data_inicio,
        models.Transaction.date <= data_fim
    ).all()
    
    # Agrupar por período
    periodos = defaultdict(lambda: {'receitas': 0, 'despesas': 0, 'quantidade': 0})
    
    for t in transacoes:
        # Determinar chave do período
        if agrupar_por == "day":
            periodo_key = t.date.strftime("%Y-%m-%d")
        elif agrupar_por == "week":
            periodo_key = t.date.strftime("%Y-W%W")
        else:  # month
            periodo_key = t.date.strftime("%Y-%m")
        
        if t.type == 'income':
            periodos[periodo_key]['receitas'] += t.amount
        else:
            periodos[periodo_key]['despesas'] += t.amount
        periodos[periodo_key]['quantidade'] += 1
    
    # Converter para lista de PeriodoStats
    evolucao = []
    for periodo, dados in sorted(periodos.items()):
        evolucao.append(schemas.PeriodoStats(
            periodo=periodo,
            receitas=dados['receitas'],
            despesas=dados['despesas'],
            saldo=dados['receitas'] - dados['despesas'],
            quantidade=dados['quantidade']
        ))
    
    return transacoes, evolucao

