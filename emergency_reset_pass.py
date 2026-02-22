"""
Script de Emergência — Redefinir Senha do Admin
Uso: python3 emergency_reset_pass.py
Este script redefine apenas a senha do usuário 'admin' para 'admin123'.
"""
import os
import sys

# Adicionar o diretório atual ao path para importar módulos do backend
sys.path.append(os.getcwd())

try:
    from backend.database import SessionLocal
    from backend.models import User
    from backend.auth import get_password_hash
    from sqlalchemy.orm import Session

    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()

    if admin_user:
        new_pass = "admin123"
        admin_user.password_hash = get_password_hash(new_pass)
        db.commit()
        print(f"✅ SUCESSO: A senha do usuário '{admin_user.username}' foi resetada para: {new_pass}")
    else:
        print("❌ ERRO: Usuário 'admin' não encontrado no banco de dados.")
    
    db.close()

except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    print("\n💡 Tente rodar dentro da pasta raiz do projeto usando: python3 emergency_reset_pass.py")
