"""
Script de migração para adicionar parent_id à tabela users
"""
import sqlite3
import os
from pathlib import Path

# Caminho do banco de dados
DATA_DIR = Path(__file__).parent / "data"
DB_NAME = "financeiro.db"
DB_PATH = DATA_DIR / DB_NAME

def migrate():
    """Executar migração do banco de dados"""
    
    print(f"[INFO] Conectando ao banco de dados: {DB_PATH}")
    if not DB_PATH.exists():
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna parent_id já existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'parent_id' in columns:
            print("[AVISO] A coluna parent_id já existe em users.")
        else:
            print("[INFO] Adicionando coluna parent_id a tabela users...")
            
            # Adicionar coluna parent_id
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN parent_id INTEGER DEFAULT NULL REFERENCES users(id)
            """)
            
            # Indice para performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_parent_id 
                ON users(parent_id)
            """)
            
            print("[OK] Coluna parent_id adicionada com sucesso.")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a migração: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRAÇÃO: Adicionar parent_id a tabela users")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\n[SUCESSO] Migração concluída!")
    else:
        print("\n[ERRO] Falha na migração.")
