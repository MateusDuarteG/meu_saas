from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, state_machine, auth
import os
from fastapi.security import OAuth2PasswordRequestForm
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS OS & Cobrança API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login")
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail informado no campo 'username' do form
    usuario = db.query(models.UsuarioModel).filter(models.UsuarioModel.email == form_data.username).first()
    
    # Valida se o usuário existe e se a senha confere
    if not usuario or usuario.senha_hash != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Retorna o token de acesso simulado para o MVP
    return {
        "access_token": f"jwt-token-valido-para-{usuario.email}",
        "token_type": "bearer"
    }

@app.post("/os/", status_code=status.HTTP_201_CREATED)
def criar_ordem_servico(
    os_data: schemas.OSCreate,
    db: Session = Depends(get_db),
    usuario_atual: models.UsuarioModel = Depends(auth.obter_usuario_atual)
):
    # Garante que o cliente pertence à mesma empresa do usuário logado
    cliente = db.query(models.ClienteModel).filter(
        models.ClienteModel.id == os_data.cliente_id,
        models.ClienteModel.empresa_id == usuario_atual.empresa_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")

    codigo_gerado = f"OS-{int(datetime.utcnow().timestamp())}"
    nova_os = models.OrdemServicoModel(
        codigo_os=codigo_gerado,
        equipamento=os_data.equipamento,
        defeito_relatado=os_data.defeito_relatado,
        valor=os_data.valor,
        status="ABERTO",
        cliente_id=os_data.cliente_id,
        empresa_id=usuario_atual.empresa_id
    )
    
    db.add(nova_os)
    db.commit()
    db.refresh(nova_os)
    return nova_os

@app.patch("/os/{os_id}/status")
def alterar_status_os(
    os_id: int,
    atualizacao: schemas.OSUpdateStatus,
    db: Session = Depends(get_db),
    usuario_atual: models.UsuarioModel = Depends(auth.obter_usuario_atual)
):
    os_item = db.query(models.OrdemServicoModel).filter(
        models.OrdemServicoModel.id == os_id,
        models.OrdemServicoModel.empresa_id == usuario_atual.empresa_id
    ).first()

    if not os_item:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

    # Valida a máquina de estados
    state_machine.validar_transicao_status(os_item.status, atualizacao.novo_status)

    os_item.status = atualizacao.novo_status
    if atualizacao.laudo_tecnico:
        os_item.laudo_tecnico = atualizacao.laudo_tecnico

    db.commit()
    db.refresh(os_item)
    return {"mensagem": f"Status atualizado para {os_item.status}", "os": os_item}

@app.get("/portal-cliente/{codigo_os}")
def portal_publico_cliente(codigo_os: str, db: Session = Depends(get_db)):
    os_item = db.query(models.OrdemServicoModel).filter(
        models.OrdemServicoModel.codigo_os == codigo_os.upper()
    ).first()

    if not os_item:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    # Tratamento seguro para o nome da empresa
    nome_empresa = "Assistência Tech"
    if hasattr(os_item, 'empresa') and os_item.empresa:
        nome_empresa = getattr(os_item.empresa, 'nome_fantasia', getattr(os_item.empresa, 'nome', "Assistência Tech"))

    return {
        "codigo_os": os_item.codigo_os,
        "equipamento": os_item.equipamento,
        "defeito_relatado": os_item.defeito_relatado,
        "status": os_item.status,
        "valor": os_item.valor,
        "laudo_tecnico": os_item.laudo_tecnico,
        "empresa": nome_empresa
    }

@app.post("/clientes/", status_code=201)
def criar_cliente(
    cliente_data: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    usuario_atual: models.UsuarioModel = Depends(auth.obter_usuario_atual)
):
    novo_cliente = models.ClienteModel(
        nome=cliente_data.nome,
        telefone=cliente_data.telefone,
        email=cliente_data.email,
        cpf_cnpj=cliente_data.cpf_cnpj,
        empresa_id=usuario_atual.empresa_id
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return {"mensagem": "Cliente cadastrado com sucesso!", "cliente": novo_cliente}

# GET /os/ -> Listar todas as OS da empresa do usuário logado
@app.get("/os/", status_code=status.HTTP_200_OK)
def listar_ordens_servico(
    db: Session = Depends(get_db),
    usuario_atual: models.UsuarioModel = Depends(auth.obter_usuario_atual)
):
    ordens = db.query(models.OrdemServicoModel).filter(
        models.OrdemServicoModel.empresa_id == usuario_atual.empresa_id
    ).all()
    return ordens

# GET /clientes/ -> Listar todos os clientes da empresa
@app.get("/clientes/", status_code=status.HTTP_200_OK)
def listar_clientes(
    db: Session = Depends(get_db),
    usuario_atual: models.UsuarioModel = Depends(auth.obter_usuario_atual)
):
    clientes = db.query(models.ClienteModel).filter(
        models.ClienteModel.empresa_id == usuario_atual.empresa_id
    ).all()
    return clientes

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.main.run("main:app", host="0.0.0.0", port=port)