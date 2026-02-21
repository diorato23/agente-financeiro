"""
Script de Reset de Banco de Dados v3 — Limpeza e Reinicialização.
Este script apaga o banco atual e recria todas as tabelas com as novas regras de Admin Único.
Ejecutar na VPS: python3 reset_db_v3.py
"""
import sqlite3
import os
import shutil

# Configurações de Caminho
DB_PATH = os.getenv("DATABASE_URL", "backend/data/financeiro.db").replace("sqlite:///", "")
if not os.path.exists(DB_PATH):
    # Fallback
    if os.path.exists("data/financeiro.db"): DB_PATH = "data/financeiro.db"
    elif os.path.exists("financeiro.db"): DB_PATH = "financeiro.db"

BACKUP_PATH = DB_PATH + ".bak"

print(f"🔄 Iniciando Reset de Banco de Dados: {DB_PATH}")

# 1. Backup de Segurança
if os.path.exists(DB_PATH):
    print(f"📦 Criando backup em: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    
    # 2. Remover Banco Antigo
    print("🗑️ Removendo banco de dados atual...")
    os.remove(DB_PATH)

# 3. Recriar usando o sistema do próprio backend (se disponível) ou via SQL direto
print("🏗️ Recriando tabelas...")

# Conectar para criar o arquivo (o SQLAlchemy cuidará do resto ao subir o app,
# mas vamos rodar o check_db_status se possível)
try:
    from backend.database import engine, Base
    from backend.models import User, Transaction, Category, Budget
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas recriadas via SQLAlchemy Core.")
    
    # Criar admin padrão
    from sqlalchemy.orm import Session
    from backend.auth import get_password_hash
    from backend.database import SessionLocal
    
    db = SessionLocal()
    default_pass = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")
    admin = User(
        username="admin",
        email="admin@financeiro.com",
        password_hash=get_password_hash(default_pass),
        role="admin",
        is_active=True,
        is_subscriber=True,
        currency="COP"
    )
    db.add(admin)
    db.commit()
    print(f"👑 Admin padrão criado: admin / {default_pass}")
    db.close()

except ImportError:
    print("⚠️ Não foi possível carregar módulos do backend. Rodando via comandos de sistema.")
    os.system("python3 -c 'from backend.database import Base, engine; Base.metadata.create_all(bind=engine)'")
    os.system("python3 -c 'from backend.auth import create_default_admin; from backend.database import SessionLocal; create_default_admin(SessionLocal())'")

print("\n✨ Reset concluído com sucesso! Agora o sistema segue as regras de Admin Único e 4 Dependentes.")
print("💡 Dica: Verifique se o arquivo .env tem a senha ADMIN_DEFAULT_PASSWORD desejada.")
