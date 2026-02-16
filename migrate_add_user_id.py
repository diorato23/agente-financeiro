"""
Script de migração para adicionar user_id às tabelas existentes
e atribuir todos os dados ao primeiro usuário (admin)
"""
import sqlite3
import os
from pathlib import Path

# Caminho do banco de dados
DATA_DIR = Path(__file__).parent / "data"
DB_NAME = "financeiro.db"  # Nome usado em backend/database.py
DB_PATH = DATA_DIR / DB_NAME

def migrate():
    """Executar migração do banco de dados"""
    
    # Determinar qual banco de dados usar
    db_path_to_use = DB_PATH
    
    if not db_path_to_use.exists():
        # Tentar nome alternativo antigo
        alt_db_path = DATA_DIR / "agente_financeiro.db"
        if alt_db_path.exists():
            print(f"[INFO] Banco encontrado com nome antigo: {alt_db_path}")
            print(f"[INFO] Renomeando para o padrao atual: {db_path_to_use}")
            try:
                os.rename(alt_db_path, db_path_to_use)
            except Exception as e:
                print(f"[ERRO] Falha ao renomear banco: {e}")
                # Usar o nome alternativo se não conseguir renomear
                db_path_to_use = alt_db_path
        else:
            print(f"[ERRO] Banco de dados nao encontrado em: {db_path_to_use}")
            print(f"       Conteudo da pasta data: {list(DATA_DIR.glob('*')) if DATA_DIR.exists() else 'Pasta data nao existe'}")
            return False
    
    print(f"[INFO] Conectando ao banco de dados: {db_path_to_use}")
    conn = sqlite3.connect(db_path_to_use)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar se a tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("[INFO] Tabela 'users' nao encontrada. Criando tabela...")
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
            cursor.execute("CREATE INDEX ix_users_username ON users (username)")
            cursor.execute("CREATE INDEX ix_users_email ON users (email)")
            print("[OK] Tabela 'users' criada com sucesso.")

        # 2. Verificar/Criar usuário admin
        cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("[INFO] Criando usuario admin padrao para assumir os dados...")
            # Hash para "admin123" (gerado via passlib ou fixo para simplificar no script)
            # Usando um hash bcrypt válido para "admin123"
            default_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES ('admin', 'admin@localhost', ?, 'admin', 1)
            """, (default_hash,))
            admin_id = cursor.lastrowid
            print(f"[OK] Usuario admin criado com ID: {admin_id}")
        else:
            admin_id = admin_user[0]
            print(f"[OK] Usuario admin encontrado (ID: {admin_id})")
        
        # 2. Verificar se a coluna user_id já existe em transactions
        cursor.execute("PRAGMA table_info(transactions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("[AVISO] A coluna user_id ja existe em transactions. Migracao ja foi executada?")
        else:
            print("[INFO] Adicionando coluna user_id a tabela transactions...")
            
            # Adicionar coluna user_id
            cursor.execute(f"""
                ALTER TABLE transactions 
                ADD COLUMN user_id INTEGER DEFAULT {admin_id} NOT NULL
            """)
            
            # Criar índice
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
                ON transactions(user_id)
            """)
            
            print(f"[OK] Coluna user_id adicionada a transactions (todos os registros atribuidos ao usuario {admin_id})")
        
        # 3. Migrar tabela budgets
        cursor.execute("PRAGMA table_info(budgets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("[AVISO] A coluna user_id ja existe em budgets.")
        else:
            print("[INFO] Adicionando coluna user_id a tabela budgets...")
            
            cursor.execute(f"""
                ALTER TABLE budgets 
                ADD COLUMN user_id INTEGER DEFAULT {admin_id} NOT NULL
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_budgets_user_id 
                ON budgets(user_id)
            """)
            
            # Remover constraint UNIQUE da coluna category (SQLite não suporta DROP CONSTRAINT diretamente)
            # Precisamos recriar a tabela
            print("[INFO] Removendo constraint UNIQUE de budgets.category...")
            
            # Criar tabela temporária
            cursor.execute(f"""
                CREATE TABLE budgets_new (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    limit_amount REAL,
                    user_id INTEGER NOT NULL DEFAULT {admin_id}
                )
            """)
            
            # Copiar dados
            cursor.execute("""
                INSERT INTO budgets_new (id, category, limit_amount, user_id)
                SELECT id, category, limit_amount, user_id FROM budgets
            """)
            
            # Remover tabela antiga e renomear
            cursor.execute("DROP TABLE budgets")
            cursor.execute("ALTER TABLE budgets_new RENAME TO budgets")
            
            # Criar índices
            cursor.execute("CREATE INDEX idx_budgets_category ON budgets(category)")
            cursor.execute("CREATE INDEX idx_budgets_user_id ON budgets(user_id)")
            
            print(f"[OK] Coluna user_id adicionada a budgets (todos os registros atribuidos ao usuario {admin_id})")
        
        # 4. Migrar tabela categories
        cursor.execute("PRAGMA table_info(categories)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("[AVISO] A coluna user_id ja existe em categories.")
        else:
            print("[INFO] Adicionando coluna user_id a tabela categories...")
            
            # Remover constraint UNIQUE e adicionar user_id
            print("[INFO] Removendo constraint UNIQUE de categories.name...")
            
            # Criar tabela temporária
            cursor.execute(f"""
                CREATE TABLE categories_new (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    user_id INTEGER NOT NULL DEFAULT {admin_id}
                )
            """)
            
            # Copiar dados
            cursor.execute("""
                INSERT INTO categories_new (id, name, user_id)
                SELECT id, name, ? FROM categories
            """, (admin_id,))
            
            # Remover tabela antiga e renomear
            cursor.execute("DROP TABLE categories")
            cursor.execute("ALTER TABLE categories_new RENAME TO categories")
            
            # Criar índices
            cursor.execute("CREATE INDEX idx_categories_name ON categories(name)")
            cursor.execute("CREATE INDEX idx_categories_user_id ON categories(user_id)")
            
            print(f"[OK] Coluna user_id adicionada a categories (todos os registros atribuidos ao usuario {admin_id})")
        
        # Commit das mudanças
        conn.commit()
        
        # 5. Verificar resultados
        print("\n[INFO] Resumo da migracao:")
        
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (admin_id,))
        trans_count = cursor.fetchone()[0]
        print(f"   - Transacoes migradas: {trans_count}")
        
        cursor.execute("SELECT COUNT(*) FROM budgets WHERE user_id = ?", (admin_id,))
        budget_count = cursor.fetchone()[0]
        print(f"   - Budgets migrados: {budget_count}")
        
        cursor.execute("SELECT COUNT(*) FROM categories WHERE user_id = ?", (admin_id,))
        cat_count = cursor.fetchone()[0]
        print(f"   - Categorias migradas: {cat_count}")
        
        print("\n[OK] Migracao concluida com sucesso!")
        print(f"   Todos os dados foram atribuidos ao usuario ID {admin_id}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a migracao: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACAO: Adicionar user_id as tabelas")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\n[SUCESSO] Migracao bem-sucedida!")
        print("   Voce pode agora executar o aplicativo normalmente.")
    else:
        print("\n[AVISO] Migracao falhou ou foi cancelada.")
        print("   Por favor, verifique os erros acima.")

