from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import os
from .database import SessionLocal
from . import models

# Configurações do Token de Convite
INVITE_SECRET_KEY = os.getenv("SECRET_KEY") # Usa a mesma chave por enquanto
ALGORITHM = "HS256"
INVITE_EXPIRE_MINUTES = 60 * 24 # 24 horas

def create_invite_token(parent_id: int):
    expire = datetime.utcnow() + timedelta(minutes=INVITE_EXPIRE_MINUTES)
    to_encode = {"sub": str(parent_id), "type": "invite", "exp": expire}
    encoded_jwt = jwt.encode(to_encode, INVITE_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_invite_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, INVITE_SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        parent_id = payload.get("sub")
        
        if token_type != "invite" or parent_id is None:
            return None
            
        return int(parent_id)
    except JWTError:
        return None

def check_dependent_limit(parent_id: int, limit: int = 4) -> bool:
    db = SessionLocal()
    try:
        count = db.query(models.User).filter(models.User.parent_id == parent_id).count()
        return count < limit
    finally:
        db.close()
