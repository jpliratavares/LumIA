from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os

# Adiciona o diretório raiz ao sys.path para encontrar o módulo orchestrator
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator.router import rotear

router = APIRouter()

# Modelo Pydantic para o corpo da requisição
class QuestionRequest(BaseModel):
    question: str

# Modelo Pydantic para a resposta
class AnswerResponse(BaseModel):
    answer: str

@router.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """ Recebe uma pergunta e a roteia para o orquestrador para obter uma resposta. """
    if not request.question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        print(f"Recebida pergunta: {request.question}")
        resposta = rotear(request.question)
        print(f"Enviando resposta: {resposta}")
        return AnswerResponse(answer=resposta)
    except Exception as e:
        # Log do erro no servidor
        print(f"Erro ao processar a pergunta '{request.question}': {e}")
        # Retorna um erro genérico para o cliente
        raise HTTPException(status_code=500, detail="Ocorreu um erro interno ao processar sua pergunta.") 