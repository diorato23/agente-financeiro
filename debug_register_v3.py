from backend.database import SessionLocal
from backend import crud, schemas, auth, models
from sqlalchemy.exc import IntegrityError
import traceback

def test_register():
    db = SessionLocal()
    user_data = schemas.UserCreate(
        username="Rafa_Test_" + str(auth.datetime.utcnow().timestamp()),
        password="Password123!",
        full_name="Rafael Test",
        phone="123456789",
        email=None,
        birth_date=None,
        currency="COP",
        role="user"
    )
    
    password_hash = auth.get_password_hash(user_data.password)
    
    try:
        print("Tentando criar usuário...")
        new_user = crud.create_user(db=db, user=user_data, password_hash=password_hash)
        print(f"Usuário criado com sucesso: {new_user.username}")
    except Exception as e:
        print("FALHA na criação do usuário!")
        print(f"Erro: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_register()
