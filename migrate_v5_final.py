"""
Migración v5 Final — Sincroniza todas las columnas posibles para evitar Errores 500.
Ejecutar en la VPS: python3 migrate_v5_final.py
"""
import sqlite3
import os

# Determinar a rota do banco
DB_PATH = os.getenv("DATABASE_URL", "backend/data/financeiro.db").replace("sqlite:///", "")
if not os.path.exists(DB_PATH):
    # fallback: busca na raiz do projeto se estiver rodando fora da pasta backend
    DB_PATH = "data/financeiro.db"
    if not os.path.exists(DB_PATH):
        DB_PATH = "financeiro.db"

print(f"[INFO] Conectando ao banco: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def migrate_table(table_name, migrations):
    print(f"\n--- Verificando tabela: {table_name} ---")
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {row[1] for row in cursor.fetchall()}
    except Exception as e:
        print(f"[ERRO] Falha ao ler tabela {table_name}: {e}")
        return

    for col, sql in migrations:
        if col not in existing_columns:
            try:
                cursor.execute(sql)
                print(f"[OK] Coluna '{col}' adicionada em {table_name}.")
            except sqlite3.OperationalError as e:
                print(f"[ERRO] {table_name}.{col}: {e}")
        else:
            print(f"[SKIP] Coluna '{col}' já existe em {table_name}.")

# 1. Migração da tabela USERS
user_migrations = [
    ("is_subscriber", "ALTER TABLE users ADD COLUMN is_subscriber BOOLEAN DEFAULT 1"),
    ("full_name",     "ALTER TABLE users ADD COLUMN full_name TEXT"),
    ("phone",         "ALTER TABLE users ADD COLUMN phone TEXT"),
    ("birth_date",    "ALTER TABLE users ADD COLUMN birth_date DATE"),
    ("currency",      "ALTER TABLE users ADD COLUMN currency TEXT DEFAULT 'COP'"),
    ("created_at",    "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
    ("parent_id",     "ALTER TABLE users ADD COLUMN parent_id INTEGER REFERENCES users(id)"),
    ("role",          "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'"),
    ("is_active",     "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
]

# 2. Migração da tabela TRANSACTIONS
tx_migrations = [
    ("is_recurring",      "ALTER TABLE transactions ADD COLUMN is_recurring BOOLEAN DEFAULT 0"),
    ("recurrence_day",    "ALTER TABLE transactions ADD COLUMN recurrence_day INTEGER"),
    ("recurrence_active", "ALTER TABLE transactions ADD COLUMN recurrence_active BOOLEAN DEFAULT 1")
]

migrate_table("users", user_migrations)
migrate_table("transactions", tx_migrations)

conn.commit()
conn.close()
print("\n✅ Migração concluída com sucesso! Reinicie o servidor para carregar as mudanças.")
