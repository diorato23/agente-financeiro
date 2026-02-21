from backend.database import SessionLocal
from backend import crud, schemas, auth, models
import traceback

def test_flow():
    db = SessionLocal()
    username = "Rafa" # O que o usuário está tentando
    password = "somepassword"
    
    print(f"--- Testando registro para {username} ---")
    
    # 1. Check existing
    try:
        existing = crud.get_user_by_username(db, username)
        if existing:
            print(f"Check: USUÁRIO JÁ EXISTE (ID: {existing.id}). Deveria retornar 400.")
        else:
            print("Check: Usuário não encontrado. Continuando...")
    except Exception as e:
        print(f"Check: ERRO ao buscar usuário: {e}")
        traceback.print_exc()
        return

    # 2. Try create (simulating the register route's try/except)
    user_in = schemas.UserCreate(
        username=username,
        password=password,
        full_name="Rafael Test",
        phone="123",
        email=None,
        currency="COP",
        role="admin"
    )
    
    password_hash = auth.get_password_hash(password)
    
    try:
        print("Executando crud.create_user...")
        new_user = crud.create_user(db=db, user=user_in, password_hash=password_hash)
        print(f"Sucesso inesperado: Criado ID {new_user.id}")
    except Exception as e:
        print(f"FALHA ESPERADA (ou não) em create_user: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_flow()
