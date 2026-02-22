import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Garantir que o caminho do banco seja sempre relativo à raiz do projeto ou absoluto conforme ENV
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    # Se não houver ENV, forçar pasta data para evitar dispersão do DB
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(BASE_DIR)
    DATA_DIR = os.path.join(PARENT_DIR, "data")
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
        except:
            pass
    DB_PATH = os.path.join(DATA_DIR, "financeiro.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
