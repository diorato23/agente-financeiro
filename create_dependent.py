import sys
import getpass
from backend import database, crud, models, schemas, auth

def create_dependent_interactive():
    db = database.SessionLocal()
    try:
        print("=== Criar Usuário Dependente ===")
        
        # 1. Identificar o usuário Pai
        parent_username = input("Digite o username do PAI (Admin): ").strip()
        parent = crud.get_user_by_username(db, parent_username)
        
        if not parent:
            print(f"[ERRO] Usuário pai '{parent_username}' não encontrado.")
            return

        print(f"[INFO] Pai encontrado: ID {parent.id} ({parent.email})")
        
        # 2. Verificar quantos dependentes já existem
        dependents = db.query(models.User).filter(models.User.parent_id == parent.id).all()
        print(f"[INFO] Dependentes atuais: {len(dependents)}/4")
        if dependents:
            for d in dependents:
                print(f"   - {d.username}")
        
        if len(dependents) >= 4:
            print("[ERRO] Limite de 4 dependentes atingido!")
            return

        # 3. Coletar dados do dependente
        username = input("Username do dependente: ").strip()
        email = input("Email do dependente (opcional, enter para pular): ").strip() or None
        password = getpass.getpass("Senha do dependente: ").strip()
        confirm = getpass.getpass("Confirme a senha: ").strip()
        
        if password != confirm:
            print("[ERRO] As senhas não coincidem.")
            return
            
        if not username or not password:
            print("[ERRO] Username e senha são obrigatórios.")
            return

        # 4. Criar
        user_in = schemas.UserCreate(
            username=username,
            email=email,
            password=password,
            role="user",
            is_active=True,
            parent_id=parent.id
        )
        
        password_hash = auth.get_password_hash(password)
        
        try:
            new_user = crud.create_user(db, user_in, password_hash)
            print(f"\n[SUCESSO] Dependente '{new_user.username}' criado com ID {new_user.id} vinculado ao Pai ID {parent.id}")
        except ValueError as e:
            print(f"\n[ERRO] {e}")
        except Exception as e:
            print(f"\n[ERRO] Falha ao criar usuário: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    create_dependent_interactive()
