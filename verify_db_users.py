"""
Script de Diagnóstico — Verifica a saúde da tabela de usuários.
Ejecutar na VPS: python3 verify_db_users.py
"""
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "backend/data/financeiro.db").replace("sqlite:///", "")
if not os.path.exists(DB_PATH):
    DB_PATH = "data/financeiro.db"
    if not os.path.exists(DB_PATH):
        DB_PATH = "financeiro.db"

print(f"🔍 Diagnosticando banco: {DB_PATH}\n")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Colunas
cursor.execute("PRAGMA table_info(users)")
columns = {row[1]: row[2] for row in cursor.fetchall()}
required = ['id', 'username', 'role', 'is_active', 'is_subscriber', 'created_at']

print("--- Estrutura da Tabela ---")
for col in required:
    status = "✅ OK" if col in columns else "❌ FALTANDO"
    print(f"Coluna {col}: {status} ({columns.get(col, 'N/A')})")

# 2. Dados Críticos (NULLs)
print("\n--- Integridade dos Dados (Null Check) ---")
cursor.execute("SELECT id, username, role, is_active, is_subscriber, created_at FROM users")
rows = cursor.fetchall()

null_found = False
for row in rows:
    uid, name, role, active, sub, created = row
    issues = []
    if role is None: issues.append("role IS NULL")
    if active is None: issues.append("is_active IS NULL")
    if sub is None: issues.append("is_subscriber IS NULL")
    if created is None: issues.append("created_at IS NULL")
    
    if issues:
        print(f"⚠️ Usuário ID {uid} ({name}) tem problemas: {', '.join(issues)}")
        null_found = True

if not null_found:
    print("✅ Nenhum valor NULL crítico encontrado em usuários existentes.")
else:
    print("\n💡 Dica: O novo schema do Pydantic que acabei de enviar lidará com esses NULLs com segurança.")

conn.close()
