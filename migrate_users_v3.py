import sqlite3
import os
import sys

# Caminho do banco de dados
DB_PATH = os.path.join("data", "financeiro.db")

def migrate():
    print(f"🚀 Iniciando migração do banco de dados: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Erro: Banco de dados não encontrado em {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Colunas que devem existir na tabela 'users'
    expected_columns = [
        ("parent_id", "INTEGER DEFAULT NULL"),
        ("full_name", "VARCHAR"),
        ("phone", "VARCHAR"),
        ("birth_date", "DATE"),
        ("currency", "VARCHAR DEFAULT 'COP'"),
        ("is_subscriber", "BOOLEAN DEFAULT 0")
    ]
    
    try:
        # Obter colunas atuais
        cursor.execute("PRAGMA table_info(users)")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        for col_name, col_type in expected_columns:
            if col_name not in existing_columns:
                print(f"➕ Adicionando coluna: {col_name} ({col_type})")
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️ Aviso ao adicionar {col_name}: {e}")
            else:
                print(f"✅ Coluna já existe: {col_name}")
        
        # Criar índice para parent_id se não existir
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_parent_id ON users(parent_id)")
        
        conn.commit()
        print("🎉 Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro fatal durante a migração: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate()
    if not success:
        sys.exit(1)
