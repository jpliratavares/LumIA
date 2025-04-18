from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
from typing import List, Optional # Importar List e Optional

# Adiciona o diretório raiz ao sys.path para encontrar o módulo orchestrator
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator.router import rotear

router = APIRouter()

# Modelo Pydantic para o corpo da requisição
class QuestionRequest(BaseModel):
    question: str

# Modelo Pydantic DETALHADO para a resposta
class DetailedAnswerResponse(BaseModel):
    answer: str # A resposta final para o usuário (pode ser msg de erro)
    raw_answer: Optional[str] = None # Resposta crua do DB, se aplicável
    logs: List[str] = [] # Logs dos passos executados

# Modelo antigo - não mais usado diretamente na resposta da rota
# class AnswerResponse(BaseModel):
#     answer: str

@router.post("/ask", response_model=DetailedAnswerResponse)
async def ask_question(request: QuestionRequest):
    """ Recebe uma pergunta, roteia e retorna uma resposta detalhada com logs. """
    if not request.question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    try:
        print(f"API Route: Recebida pergunta: {request.question}")
        # O orquestrador agora retorna um Dict ou None
        result_dict = await rotear(request.question)

        if result_dict:
            print(f"API Route: Recebido resultado do orquestrador. Enviando resposta detalhada.")
            # Desempacota o dicionário no modelo Pydantic
            # Garante que os campos opcionais sejam None se não presentes
            return DetailedAnswerResponse(
                answer=result_dict.get("answer", "Erro: Resposta final não encontrada no resultado."),
                raw_answer=result_dict.get("raw_answer"), # Será None se não existir no dict
                logs=result_dict.get("logs", []) # Será lista vazia se não existir
            )
        else:
            # Caso raro onde o orquestrador falha em retornar até mesmo uma resposta de fallback
            print("API Route: Orquestrador retornou None. Enviando erro genérico.")
            return DetailedAnswerResponse(
                answer="Desculpe, não consegui processar sua pergunta no momento.",
                logs=["Error: Orchestrator failed to return a response."]
            )

    except Exception as e:
        print(f"API Route: Erro inesperado ao processar a pergunta '{request.question}': {e}")
        # Em caso de erro na própria rota/orquestrador, retorna uma resposta de erro detalhada
        # Não usamos HTTPException aqui para manter o formato DetailedAnswerResponse
        return DetailedAnswerResponse(
            answer="Desculpe, ocorreu um erro interno grave ao processar sua pergunta.",
            logs=[f"Exception: {type(e).__name__}: {e}"]
        ) 