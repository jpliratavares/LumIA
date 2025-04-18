from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
import time # Importa o módulo time
from typing import List, Optional # Importar List e Optional

# Adiciona o diretório raiz ao sys.path para encontrar o módulo orchestrator
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator.router import rotear
# Importa a constante do modelo do LLM Agent para saber qual foi usado
from agents.llm_agent import GROQ_MODEL

router = APIRouter()

# Modelo Pydantic para o corpo da requisição
class QuestionRequest(BaseModel):
    question: str

# Modelo Pydantic DETALHADO para a resposta
class DetailedAnswerResponse(BaseModel):
    answer: str # A resposta final para o usuário (pode ser msg de erro)
    raw_answer: Optional[str] = None # Resposta crua do DB, se aplicável
    logs: List[str] = [] # Logs dos passos executados
    processing_time_ms: float # Adiciona campo para tempo de processamento
    model_used: Optional[str] = None # Adiciona campo para o modelo

# Modelo antigo - não mais usado diretamente na resposta da rota
# class AnswerResponse(BaseModel):
#     answer: str

@router.post("/ask", response_model=DetailedAnswerResponse)
async def ask_question(request: QuestionRequest):
    """ Recebe uma pergunta, roteia, mede o tempo e retorna resposta detalhada com modelo. """
    start_time = time.perf_counter() # Marca o tempo de início

    if not request.question:
        # Embora seja um erro 400, ainda podemos calcular o tempo
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        # Lança a exceção normalmente, mas o tempo foi medido se necessário logar
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    final_response: DetailedAnswerResponse
    model_name = None # Inicializa como None
    try:
        print(f"API Route: Recebida pergunta: {request.question}")
        # O orquestrador agora retorna um Dict ou None
        result_dict = await rotear(request.question)

        end_time = time.perf_counter() # Marca o tempo de fim (sucesso)
        duration_ms = (end_time - start_time) * 1000

        if result_dict:
            # Assume que se temos um resultado do orquestrador, o LLM foi potencialmente usado
            # (seja no PrapeAgent ou como fallback geral). Em ambos os casos, é o GROQ_MODEL.
            model_name = GROQ_MODEL
            print(f"API Route: Recebido resultado. Modelo usado: {model_name}. Tempo: {duration_ms:.2f} ms")
            # Desempacota o dicionário no modelo Pydantic
            # Garante que os campos opcionais sejam None se não presentes
            final_response = DetailedAnswerResponse(
                answer=result_dict.get("answer", "Erro: Resposta final não encontrada no resultado."),
                raw_answer=result_dict.get("raw_answer"), # Será None se não existir no dict
                logs=result_dict.get("logs", []), # Será lista vazia se não existir
                processing_time_ms=duration_ms, # Inclui o tempo na resposta
                model_used=model_name # Inclui o nome do modelo
            )
        else:
            # Caso raro onde o orquestrador falha em retornar até mesmo uma resposta de fallback
            print("API Route: Orquestrador retornou None. Enviando erro genérico. Tempo: {duration_ms:.2f} ms")
            final_response = DetailedAnswerResponse(
                answer="Desculpe, não consegui processar sua pergunta no momento.",
                logs=["Error: Orchestrator failed to return a response."],
                processing_time_ms=duration_ms, # Inclui o tempo na resposta de erro
                model_used=None # Nenhum modelo foi usado
            )

    except Exception as e:
        end_time = time.perf_counter() # Marca o tempo de fim (exceção)
        duration_ms = (end_time - start_time) * 1000
        print(f"API Route: Erro inesperado. Tempo: {duration_ms:.2f} ms. Erro: {e}")
        # Em caso de erro na própria rota/orquestrador, retorna uma resposta de erro detalhada
        # Não usamos HTTPException aqui para manter o formato DetailedAnswerResponse
        final_response = DetailedAnswerResponse(
            answer="Desculpe, ocorreu um erro interno grave ao processar sua pergunta.",
            logs=[f"Exception: {type(e).__name__}: {e}"],
            processing_time_ms=duration_ms, # Inclui o tempo na resposta de erro
            model_used=None # Nenhum modelo foi confirmado como usado devido ao erro
        )

    return final_response 