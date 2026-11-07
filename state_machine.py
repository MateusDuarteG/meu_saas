from fastapi import HTTPException

# Transições permitidas na Máquina de Estados
TRANSIÇÕES_PERMITIDAS = {
    "ABERTO": ["ORCAMENTO", "CANCELADO"],
    "ORCAMENTO": ["EM_EXECUCAO", "CANCELADO"],
    "EM_EXECUCAO": ["AGUARDANDO_PAGAMENTO", "CANCELADO"],
    "AGUARDANDO_PAGAMENTO": ["CONCLUIDO"],
    "CONCLUIDO": [],
    "CANCELADO": []
}

def validar_transicao_status(status_atual: str, novo_status: str):
    if novo_status not in TRANSIÇÕES_PERMITIDAS.get(status_atual, []):
        raise HTTPException(
            status_code=400,
            detail=f"Transição inválida: Não é permitido mudar de '{status_atual}' para '{novo_status}'."
        )
    return True