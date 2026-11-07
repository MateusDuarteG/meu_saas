from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ==========================================
# SCHEMAS DE USUÁRIO E EMPRESA
# ==========================================
class EmpresaCadastroCreate(BaseModel):
    nome_fantasia: str
    nome_responsavel: str
    email: EmailStr
    senha: str
    
class EmpresaCreate(BaseModel):
    nome_fantasia: str
    cnpj: str
    whatsapp: Optional[str] = None

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str = "atendente" # admin, atendente, tecnico
    empresa_id: int

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    empresa_id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


# ==========================================
# SCHEMAS DE CLIENTES
# ==========================================
class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    email: Optional[EmailStr] = None
    cpf_cnpj: Optional[str] = None

class ClienteResponse(BaseModel):
    id: int
    nome: str
    telefone: str
    email: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    empresa_id: int

    class Config:
        from_attributes = True


# ==========================================
# SCHEMAS DE ORDEM DE SERVIÇO (OS)
# ==========================================
class OSCreate(BaseModel):
    cliente_id: int
    equipamento: str
    defeito_relatado: str
    valor: float = 0.0

class OSUpdateStatus(BaseModel):
    novo_status: str # ORCAMENTO, EM_EXECUCAO, AGUARDANDO_PAGAMENTO, CONCLUIDO, CANCELADO
    laudo_tecnico: Optional[str] = None

class OSResponse(BaseModel):
    id: int
    codigo_os: str
    equipamento: str
    defeito_relatado: str
    laudo_tecnico: Optional[str] = None
    valor: float
    status: str
    cliente_id: int
    empresa_id: int
    criado_em: datetime

    class Config:
        from_attributes = True