import sqlite3
import os
from pathlib import Path

# Caminhos possíveis para o banco de dados
DB_NAMES = ["financeiro.db", "agente_financeiro.db"]
DATA_DIR_CONTAINER = Path("/app/data")
DATA_DIR_LOCAL = Path(__file__).parent / "data"

def get_db_path():
    # Tentar caminho do container primeiro
    if DATA_DIR_CONTAINER.exists():
        for db_name in DB_NAMES:
            db_path = DATA_DIR_CONTAINER / db_name
            if db_path.exists():
                return db_path
        # Se diretório existe mas arquivo não, usar padrão
        return DATA_DIR_CONTAINER / "financeiro.db"
    
    # Tentar caminho local
    if DATA_DIR_LOCAL.exists():
        for db_name in DB_NAMES:
            db_path = DATA_DIR_LOCAL / db_name
            if db_path.exists():
                return db_path
        return DATA_DIR_LOCAL / "financeiro.db"
    
    return None

def reset_admin():
    db_path = get_db_path()
    if not db_path:
        print("[ERRO] Pasta 'data' nao encontrada.")
        return

    print(f"[INFO] Usando banco de dados: {db_path}")
    
    # Garantir que o diretório existe
    os.makedirs(db_path.parent, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Verificar/Criar tabela users
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("[INFO] Tabela 'users' nao existe. Criando...")
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR UNIQUE NOT NULL,
                    email VARCHAR UNIQUE,
                    password_hash VARCHAR NOT NULL,
                    role VARCHAR DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # 2. Hash bcrypt para 'admin123'
        # Gerado via passlib.hash.bcrypt.hash("admin123")
        admin_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        
        # 3. Verificar se admin existe
        cursor.execute("SELECT id FROM users WHERE username='admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"[INFO] Usuario 'admin' encontrado (ID: {admin[0]}). Atualizando senha...")
            cursor.execute("UPDATE users SET password_hash=?, is_active=1 WHERE id=?", (admin_hash, admin[0]))
        else:
            print("[INFO] Usuario 'admin' NAO encontrado. Criando...")
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES ('admin', 'admin@localhost', ?, 'admin', 1)
            """, (admin_hash,))
            
        conn.commit()
        print("\n[SUCESSO] Senha do admin redefinida para: admin123")
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao redefinir admin: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin()
