from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database

# Configuración de seguridad
import os
SECRET_KEY = os.getenv("SECRET_KEY", "agente-financeiro-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Contexto para hash de contraseñas
# Contexto para hash de contraseñas
# Usando pbkdf2_sha256 por compatibilidad (Windows/Linux) y evitando errores de DLL de bcrypt
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    return pwd_context.verify(plain_password[:72], hashed_password)


def get_password_hash(password: str) -> str:
    """Crear hash de contraseña"""
    # Bcrypt limit is 72 bytes
    return pwd_context.hash(password[:72])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    """Dependencia para obtener sesión de base de datos"""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """Obtener usuario actual desde el token JWT"""
    if not token:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


async def get_current_user_required(
    current_user: Optional[models.User] = Depends(get_current_user)
) -> models.User:
    """Requerir usuario autenticado"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


async def require_admin(
    current_user: models.User = Depends(get_current_user_required)
) -> models.User:
    """Requerir que el usuario sea administrador (Padre)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


async def require_any_admin(
    current_user: models.User = Depends(get_current_user_required)
) -> models.User:
    """Requerir que sea admin o subadmin"""
    if current_user.role not in ["admin", "subadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes"
        )
    return current_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Autenticar usuario con username y password"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


def create_default_admin(db: Session):
    """Criar usuario admin por defecto si no existe ningún usuario"""
    existing_user = db.query(models.User).first()
    if not existing_user:
        default_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123")
        if default_password == "admin123":
            print("⚠️  AVISO: Usando senha admin padrão. Defina ADMIN_DEFAULT_PASSWORD no .env!")
        admin_user = models.User(
            username="admin",
            email="admin@localhost",
            password_hash=get_password_hash(default_password),
            role="admin",
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print(f"✅ Usuario admin creado: admin / {default_password}")

