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
        # Garantir campos básicos para evitar erros de validação
        if not admin_user.email: admin_user.email = "admin@localhost"
        admin_user.is_active = True
        admin_user.role = "admin"
        
        db.commit()
        print(f"✅ SUCESSO: O usuário '{admin_user.username}' foi atualizado e a senha resetada para: {new_pass}")
    else:
        # Se por algum motivo o admin sumiu, criar de volta
        print("💡 Usuário 'admin' não encontrado. Criando novo admin...")
        new_admin = User(
            username="admin",
            email="admin@localhost",
            password_hash=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print(f"✅ SUCESSO: Novo usuário 'admin' criado com senha: admin123")
    
    db.close()

except Exception as e:
    print(f"❌ ERRO CRÍTICO: {e}")
    print("\n💡 Tente rodar dentro da pasta raiz do projeto usando: python3 emergency_reset_pass.py")
