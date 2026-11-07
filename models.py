from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class EmpresaModel(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String(100), nullable=False)
    cnpj = Column(String(20), unique=True, index=True)
    whatsapp = Column(String(20))
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuarios = relationship("UsuarioModel", back_populates="empresa")
    clientes = relationship("ClienteModel", back_populates="empresa")
    ordens_servico = relationship("OrdemServicoModel", back_populates="empresa")


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(20), default="atendente")  # admin, atendente, tecnico
    empresa_id = Column(Integer, ForeignKey("empresas.id"))

    empresa = relationship("EmpresaModel", back_populates="usuarios")


class ClienteModel(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100))
    cpf_cnpj = Column(String(20))
    empresa_id = Column(Integer, ForeignKey("empresas.id"))

    empresa = relationship("EmpresaModel", back_populates="clientes")
    ordens_servico = relationship("OrdemServicoModel", back_populates="cliente")


class OrdemServicoModel(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True, index=True)
    codigo_os = Column(String(20), unique=True, index=True) # Ex: OS-1029
    equipamento = Column(String(100), nullable=False) # Ex: Notebook Dell Vostro 5470
    defeito_relatado = Column(Text, nullable=False)
    laudo_tecnico = Column(Text, nullable=True)
    valor = Column(Float, default=0.0)
    status = Column(String(30), default="ABERTO") # ABERTO, ORCAMENTO, EM_EXECUCAO, AGUARDANDO_PAGAMENTO, CONCLUIDO
    
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    criado_em = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("EmpresaModel", back_populates="ordens_servico")
    cliente = relationship("ClienteModel", back_populates="ordens_servico")