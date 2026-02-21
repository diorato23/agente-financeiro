"""
Migração v4 — Adiciona colunas faltantes na tabela users.
Executar na VPS: python3 migrate_users_v4.py
"""
import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "data/financeiro.db").replace("sqlite:///", "")
if not os.path.exists(DB_PATH):
    # fallback: busca na raiz
    DB_PATH = "financeiro.db"

print(f"[INFO] Conectando ao banco: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar colunas existentes
cursor.execute("PRAGMA table_info(users)")
existing_columns = {row[1] for row in cursor.fetchall()}
print(f"[INFO] Colunas existentes: {existing_columns}")

migrations = [
    ("is_subscriber", "ALTER TABLE users ADD COLUMN is_subscriber BOOLEAN DEFAULT 1"),
    ("full_name",     "ALTER TABLE users ADD COLUMN full_name TEXT"),
    ("phone",         "ALTER TABLE users ADD COLUMN phone TEXT"),
    ("birth_date",    "ALTER TABLE users ADD COLUMN birth_date DATE"),
    ("currency",      "ALTER TABLE users ADD COLUMN currency TEXT DEFAULT 'COP'"),
    ("created_at",    "ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"),
    ("parent_id",     "ALTER TABLE users ADD COLUMN parent_id INTEGER REFERENCES users(id)"),
    # Transações recorrentes
]

for col, sql in migrations:
    if col not in existing_columns:
        try:
            cursor.execute(sql)
            print(f"[OK] Coluna '{col}' adicionada.")
        except sqlite3.OperationalError as e:
            print(f"[ERRO] {col}: {e}")
    else:
        print(f"[SKIP] Coluna '{col}' já existe.")

# Migração da tabela transactions (recorrência)
cursor.execute("PRAGMA table_info(transactions)")
tx_columns = {row[1] for row in cursor.fetchall()}

tx_migrations = [
    ("is_recurring",      "ALTER TABLE transactions ADD COLUMN is_recurring BOOLEAN DEFAULT 0"),
    ("recurrence_day",    "ALTER TABLE transactions ADD COLUMN recurrence_day INTEGER"),
    ("recurrence_active", "ALTER TABLE transactions ADD COLUMN recurrence_active BOOLEAN DEFAULT 1"),
]

for col, sql in tx_migrations:
    if col not in tx_columns:
        try:
            cursor.execute(sql)
            print(f"[OK] Coluna transactions.'{col}' adicionada.")
        except sqlite3.OperationalError as e:
            print(f"[ERRO] transactions.{col}: {e}")
    else:
        print(f"[SKIP] Coluna transactions.'{col}' já existe.")

conn.commit()
conn.close()
print("\n✅ Migração concluída! Reinicie o servidor.")
