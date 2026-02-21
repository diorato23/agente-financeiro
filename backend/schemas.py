from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class TransactionBase(BaseModel):
    description: str
    amount: float
    type: str
    category: str
    date: date
    # Feature #17 — Recorrência
    is_recurring: bool = False
    recurrence_day: Optional[int] = None  # Dia do mês (1-31)
    recurrence_active: bool = True

class UserSimple(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

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
    user_id: int
    user: Optional[UserSimple] = None  # Para mostrar quem fez a transação (pai/filho)
    class Config:
        from_attributes = True


# Feature #6 — Status de Orçamento
class BudgetStatus(BaseModel):
    category: str
    limit_amount: float
    spent: float
    percentage: float
    alert: bool  # True se >= 80%
    exceeded: bool  # True se >= 100%


# Feature #3 — Analytics por Categoria
class CategoryData(BaseModel):
    category: str
    total: float
    percentage: float
    count: int

class CategoryAnalytics(BaseModel):
    period: str
    expenses_by_category: List[CategoryData]
    income_by_category: List[CategoryData]
    total_expenses: float
    total_income: float

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
    # M1 FIX: 'password' não está listado aqui — não vaza na resposta da API
    class Config:
        from_attributes = True
        # Garante que password nunca seja serializado mesmo que o ORM o carregue
        fields = {'password': {'exclude': True}}



# ============ USERS ============

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_subscriber: bool = False
    parent_id: Optional[int] = None
    
    # Novos campos
    full_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    currency: str = "COP"

class InviteResponse(BaseModel):
    invite_link: str
    token: str

class InviteInfo(BaseModel):
    parent_id: int
    parent_username: str
    current_dependents: int
    max_dependents: int = 4

class DependentRegister(BaseModel):
    token: str
    username: str
    password: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    parent_id: Optional[int] = None
    is_subscriber: Optional[bool] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    currency: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    # parent_id já herdado de UserBase
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


# ============ CATEGORIES ============

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True


# ============ TRANSACTION SEARCH & REPORTS ============

class TransactionFilter(BaseModel):
    """Schema para filtros de busca de transações"""
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    tipo: Optional[str] = None  # 'income' ou 'expense'
    categoria: Optional[str] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    busca: Optional[str] = None  # Busca textual na descrição
    ordenar_por: str = "date"  # date, amount, category
    ordem: str = "desc"  # asc ou desc
    skip: int = 0
    limit: int = 100


class TransactionStats(BaseModel):
    """Estatísticas agregadas de transações"""
    income: float
    expenses: float
    balance: float
    quantidade_transacoes: int
    quantidade_receitas: int
    quantidade_despesas: int
    media_receitas: float
    media_despesas: float
    por_categoria: dict  # {categoria: {total: float, quantidade: int}}


class TransactionSearchResponse(BaseModel):
    """Resposta de busca com transações e metadados"""
    transacoes: List[Transaction]
    total: int  # Total de registros encontrados
    pagina_atual: int
    total_paginas: int
    estatisticas: TransactionStats


class PeriodoStats(BaseModel):
    """Estatísticas de um período específico"""
    periodo: str  # "2026-01", "2026-02-14", etc
    receitas: float
    despesas: float
    saldo: float
    quantidade: int


class TransactionReport(BaseModel):
    """Relatório completo de transações"""
    data_inicio: date
    data_fim: date
    transacoes: List[Transaction]
    estatisticas: TransactionStats
    evolucao_temporal: List[PeriodoStats]  # Evolução por período
    top_categorias_despesas: List[dict]  # Top categorias de despesas
    top_categorias_receitas: List[dict]  # Top categorias de receitas
