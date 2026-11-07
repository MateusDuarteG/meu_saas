from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import models
from database import get_db

security = HTTPBearer()

def obter_usuario_atual(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    # Pega o token enviado no header
    token = credentials.credentials
    
    # Busca um usuário no banco
    usuario = db.query(models.UsuarioModel).first()
    if not usuario:
        # Cria um usuário padrão automaticamente caso o banco esteja vazio
        usuario = models.UsuarioModel(
            nome="Mateus Duarte",
            email="mateus@assistencia.com",
            senha_hash="123456",
            perfil="admin",
            empresa_id=1
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        
    return usuario