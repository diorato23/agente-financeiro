#!/usr/bin/env python3
"""
Script de migração para adicionar colunas de transações recorrentes.
Execute no VPS após atualizar o código:

    python -m backend.migrate_recurring

Ou diretamente:

    python backend/migrate_recurring.py
"""

import os
import sqlite3
from pathlib import Path

# Localizar o banco de dados
DB_PATH = os.getenv("DATABASE_URL", "").replace("sqlite:///", "") or "financeiro.db"

def migrate():
    print(f"[migração] Conectando ao banco: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"[migração] Colunas existentes: {columns}")

    # Adicionar is_recurring
    if "is_recurring" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN is_recurring BOOLEAN DEFAULT 0")
        print("[migração] ✅ Coluna 'is_recurring' adicionada")
    else:
        print("[migração] ⚠️  Coluna 'is_recurring' já existe")

    # Adicionar recurrence_day
    if "recurrence_day" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN recurrence_day INTEGER")
        print("[migração] ✅ Coluna 'recurrence_day' adicionada")
    else:
        print("[migração] ⚠️  Coluna 'recurrence_day' já existe")

    # Adicionar recurrence_active
    if "recurrence_active" not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN recurrence_active BOOLEAN DEFAULT 1")
        print("[migração] ✅ Coluna 'recurrence_active' adicionada")
    else:
        print("[migração] ⚠️  Coluna 'recurrence_active' já existe")

    conn.commit()
    conn.close()
    print("[migração] ✅ Migração concluída com sucesso!")

if __name__ == "__main__":
    migrate()
