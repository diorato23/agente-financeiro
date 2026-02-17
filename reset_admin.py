from backend.database import SessionLocal
from backend.models import User
from passlib.context import CryptContext

# Configurar contexto de senha (mesmo do auth.py ATUALIZADO)
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

def reset_admin_password():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if user:
            print(f"Usuário encontrado: {user.username}")
            new_password = "admin123"
            # Gerar hash compatível (pbkdf2_sha256)
            new_hash = pwd_context.hash(new_password)
            
            user.password_hash = new_hash
            db.commit()
            print(f"Senha atualizada para: {new_password}")
            print(f"Novo hash (inicia com...): {new_hash[:20]}...")
        else:
            print("Usuário 'admin' não encontrado.")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
