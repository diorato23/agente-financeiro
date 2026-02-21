from sqlalchemy.orm import Session
from . import models, schemas

# Transactions
def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Verificar se usuario tem dependentes
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Lista de IDs para buscar (o próprio usuario + dependentes)
    user_ids = [user_id]
    
    if user and not user.parent_id:
        # Se não é dependente (pode ser pai), buscar filhos
        children = db.query(models.User).filter(models.User.parent_id == user_id).all()
        for child in children:
            user_ids.append(child.id)
            
    return db.query(models.Transaction).filter(models.Transaction.user_id.in_(user_ids)).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.dict(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionUpdate, user_id: int):
    # Buscar transação primeiro sem filtro de user_id
    db_trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_trans:
        return None
    
    # Verificar permissão: dono da transação OU pai do dono
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_trans.user_id != user_id:
        # Se não for o dono, verificar se o dono é dependente deste usuário
        owner = db.query(models.User).filter(models.User.id == db_trans.user_id).first()
        if not (owner and owner.parent_id == user_id):
             # Ou se for um subadmin gerenciando transação da mesma família
            if not (user and user.role == "subadmin" and owner and owner.parent_id == user.parent_id):
                return None # Sem permissão

    update_data = transaction.dict(exclude_unset=True)
    # Convert date string to date object if present
    if 'date' in update_data and update_data['date']:
        from datetime import datetime
        if isinstance(update_data['date'], str):
            try:
                # Tentar vários formatos comuns se necessário, mas o padrão HTML é YYYY-MM-DD
                update_data['date'] = datetime.strptime(update_data['date'], '%Y-%m-%d').date()
            except ValueError:
                pass 

    for key, value in update_data.items():
        setattr(db_trans, key, value)
    db.commit()
    db.refresh(db_trans)
    return db_trans

def delete_transaction(db: Session, transaction_id: int, user_id: int):
    db_trans = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not db_trans:
        return None

    # Verificar permissão: dono da transação OU pai do dono
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_trans.user_id != user_id:
        owner = db.query(models.User).filter(models.User.id == db_trans.user_id).first()
        if not (owner and owner.parent_id == user_id):
            if not (user and user.role == "subadmin" and owner and owner.parent_id == user.parent_id):
                return None

    db.delete(db_trans)
    db.commit()
    return db_trans

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
        return db_budget  # BUG FIX: retorna o existente em vez de criar duplicata
    
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

    return False


# ============ CATEGORIES ============

def get_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Verificar se usuario é dependente
    user = db.query(models.User).filter(models.User.id == user_id).first()
    target_user_id = user_id
    
    if user and user.parent_id:
        # Se for dependente, usar categorias do pai
        target_user_id = user.parent_id
        
    return db.query(models.Category).filter(models.Category.user_id == target_user_id).offset(skip).limit(limit).all()

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
    # Se for dependente, verificar limite
    if user.parent_id:
        parent = db.query(models.User).filter(models.User.id == user.parent_id).first()
        if not parent:
            raise ValueError("Usuário pai não encontrado")
        
        # Verificar quantos dependentes o pai já tem
        count = db.query(models.User).filter(models.User.parent_id == user.parent_id).count()
        if count >= 4:
            raise ValueError("Limite de 4 dependentes atingido")

    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=password_hash,
        role=user.role,
        is_active=user.is_active,
        is_subscriber=user.is_subscriber,
        parent_id=user.parent_id,
        full_name=user.full_name,
        phone=user.phone,
        birth_date=user.birth_date,
        currency=user.currency
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, password_hash: str = None):
    """Actualizar usuario"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        if password_hash:
            db_user.password_hash = password_hash
        
        for key, value in update_data.items():
            if key != 'password':
                setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
    return db_user

def toggle_user_status(db: Session, user_id: int):
    """Alternar entre activo/inactivo"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.is_active = not db_user.is_active
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

def get_dependents(db: Session, user_id: int):
    """Obter dependentes de um usuário"""
    return db.query(models.User).filter(models.User.parent_id == user_id).all()


# ============ TRANSACTION SEARCH & FILTERS ============

def get_transactions_filtered(db: Session, filtros: schemas.TransactionFilter, user_id: int):
    """Buscar transações com filtros avançados"""
    from sqlalchemy import or_, and_, desc, asc
    
    # Verificar se usuário tem dependentes
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Lista de IDs para buscar (o próprio usuario + dependentes)
    user_ids = [user_id]
    
    if user and (not user.parent_id or user.role == "subadmin"):
        # Admin ou Subadmin (que pode ver tudo da família)
        query_parent_id = user_id if not user.parent_id else user.parent_id
        
        # Adiciona o ID do "pai" da família (se não for o próprio)
        if query_parent_id not in user_ids:
            user_ids.append(query_parent_id)
            
        # Buscar todos os dependentes deste pai
        children = db.query(models.User).filter(models.User.parent_id == query_parent_id).all()
        for child in children:
            if child.id not in user_ids:
                user_ids.append(child.id)
    
    query = db.query(models.Transaction).filter(models.Transaction.user_id.in_(user_ids))
    
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
            # Reutilizar lógica de IDs do get_transactions
            user = db.query(models.User).filter(models.User.id == user_id).first()
            user_ids = [user_id]
            if user and not user.parent_id:
                children = db.query(models.User).filter(models.User.parent_id == user_id).all()
                for child in children:
                    user_ids.append(child.id)
            
            transacoes = db.query(models.Transaction).filter(models.Transaction.user_id.in_(user_ids)).all()
        else:
            transacoes = db.query(models.Transaction).all()
    
    if not transacoes:
        return schemas.TransactionStats(
            income=0,
            expenses=0,
            balance=0,
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
        income=total_receitas,
        expenses=total_despesas,
        balance=total_receitas - total_despesas,
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
    
    # Verificar pai/filhos
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user_ids = [user_id]
    if user and not user.parent_id:
        children = db.query(models.User).filter(models.User.parent_id == user_id).all()
        for child in children:
            user_ids.append(child.id)
    
    transacoes = db.query(models.Transaction).filter(
        models.Transaction.user_id.in_(user_ids),
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


# ============ FEATURE #17 — TRANSAÇÕES RECORRENTES ============

def get_recurring_transactions(db: Session, user_id: int):
    """Lista todas as transações recorrentes ativas do usuário"""
    return db.query(models.Transaction).filter(
        models.Transaction.user_id == user_id,
        models.Transaction.is_recurring == True
    ).all()

def apply_recurring_transactions(db: Session, user_id: int):
    """Aplica transações recorrentes no mês atual (idempotente)"""
    from datetime import date
    today = date.today()
    current_month = today.month
    current_year = today.year

    recorrentes = get_recurring_transactions(db, user_id)
    criadas = []

    for r in recorrentes:
        if not r.recurrence_active or not r.recurrence_day:
            continue

        # Verificar se já foi aplicada este mês
        existing = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.description == r.description,
            models.Transaction.amount == r.amount,
            models.Transaction.category == r.category,
            models.Transaction.is_recurring == False,
        ).filter(
            models.Transaction.date >= date(current_year, current_month, 1)
        ).first()

        if existing:
            continue  # Já aplicada este mês

        import calendar
        ultimo_dia = calendar.monthrange(current_year, current_month)[1]
        dia = min(r.recurrence_day, ultimo_dia)
        target_date = date(current_year, current_month, dia)

        nova = models.Transaction(
            description=r.description,
            amount=r.amount,
            type=r.type,
            category=r.category,
            date=target_date,
            user_id=user_id,
            is_recurring=False,
            recurrence_day=None,
            recurrence_active=True
        )
        db.add(nova)
        criadas.append(nova)

    if criadas:
        db.commit()
        for t in criadas:
            db.refresh(t)

    return criadas


# ============ FEATURE #6 — STATUS DE ORÇAMENTO ============

def get_budget_status(db: Session, user_id: int):
    """Retorna status de todos os orçamentos com % do gasto atual no mês"""
    from datetime import date
    today = date.today()
    inicio_mes = date(today.year, today.month, 1)

    budgets = get_budgets(db, user_id)
    status_list = []

    for budget in budgets:
        spent_rows = db.query(models.Transaction).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.category == budget.category,
            models.Transaction.type == "expense",
            models.Transaction.date >= inicio_mes,
            models.Transaction.date <= today
        ).all()

        total_spent = sum(t.amount for t in spent_rows)
        percentage = (total_spent / budget.limit_amount * 100) if budget.limit_amount > 0 else 0

        status_list.append(schemas.BudgetStatus(
            category=budget.category,
            limit_amount=budget.limit_amount,
            spent=round(total_spent, 2),
            percentage=round(percentage, 1),
            alert=percentage >= 80,
            exceeded=percentage >= 100
        ))

    return status_list


# ============ FEATURE #3 — ANALYTICS POR CATEGORIA ============

def get_category_analytics(db: Session, user_id: int, period: str = None):
    """Retorna analytics de gastos e receitas agrupados por categoria"""
    from datetime import date
    import calendar

    today = date.today()

    if period:
        try:
            year, month = int(period.split("-")[0]), int(period.split("-")[1])
        except Exception:
            year, month = today.year, today.month
    else:
        year, month = today.year, today.month

    inicio = date(year, month, 1)
    ultimo_dia = calendar.monthrange(year, month)[1]
    fim = date(year, month, ultimo_dia)
    period_str = f"{year}-{month:02d}"

    user = db.query(models.User).filter(models.User.id == user_id).first()
    user_ids = [user_id]
    if user and not user.parent_id:
        children = db.query(models.User).filter(models.User.parent_id == user_id).all()
        for c in children:
            user_ids.append(c.id)

    transacoes = db.query(models.Transaction).filter(
        models.Transaction.user_id.in_(user_ids),
        models.Transaction.date >= inicio,
        models.Transaction.date <= fim
    ).all()

    despesas = {}
    receitas = {}
    total_despesas = 0.0
    total_receitas = 0.0

    for t in transacoes:
        if t.type == "expense":
            total_despesas += t.amount
            if t.category not in despesas:
                despesas[t.category] = {"total": 0.0, "count": 0}
            despesas[t.category]["total"] += t.amount
            despesas[t.category]["count"] += 1
        else:
            total_receitas += t.amount
            if t.category not in receitas:
                receitas[t.category] = {"total": 0.0, "count": 0}
            receitas[t.category]["total"] += t.amount
            receitas[t.category]["count"] += 1

    def build_list(data, total):
        result = []
        for cat, vals in sorted(data.items(), key=lambda x: x[1]["total"], reverse=True):
            result.append(schemas.CategoryData(
                category=cat,
                total=round(vals["total"], 2),
                percentage=round(vals["total"] / total * 100, 1) if total > 0 else 0,
                count=vals["count"]
            ))
        return result

    return schemas.CategoryAnalytics(
        period=period_str,
        expenses_by_category=build_list(despesas, total_despesas),
        income_by_category=build_list(receitas, total_receitas),
        total_expenses=round(total_despesas, 2),
        total_income=round(total_receitas, 2)
    )
