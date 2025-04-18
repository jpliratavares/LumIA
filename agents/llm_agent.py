import httpx
import json
import sys
import os
import sqlite3
from typing import Optional, List
import asyncio

# Adiciona o diretório raiz ao sys.path para encontrar o módulo utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.db_handler import create_connection

# --- Configuração da API LLM (agora Groq) ---
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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" # Chave fornecida
GROQ_MODEL = "llama3-8b-8192"
GROQ_TIMEOUT = 120.0 # Timeout para Groq (pode ser menor que Ollama local)

# --- Configuração do DB (mantido) ---
DB_TABLE_FOR_CONTEXT = "prape"
CONTEXT_LIMIT = 3
UFPB_TERMS = ["ufpb", "universidade federal da paraíba"]

class LLMAgent:
    """ Agente para interagir com um Large Language Model via API Groq (Async). """

    def _fetch_context_from_db(self, pergunta: str) -> List[str]:
        """ Busca contexto no DB e filtra por termos da UFPB. """
        # TODO: Melhorar a busca de contexto com busca vetorial/embeddings.
        context_list = []
        conn = create_connection()
        if conn is None:
            print("LLMAgent: Falha ao conectar ao DB para buscar contexto.")
            return context_list

        all_results = []
        try:
            cur = conn.cursor()
            termo_busca = f"%{pergunta}%"
            # Busca simples usando LIKE
            cur.execute(f"SELECT resposta FROM {DB_TABLE_FOR_CONTEXT} WHERE pergunta LIKE ? OR resposta LIKE ? LIMIT ?",
                        (termo_busca, termo_busca, CONTEXT_LIMIT))
            resultados_query = cur.fetchall()
            if resultados_query:
                all_results = [row[0] for row in resultados_query]
                print(f"LLMAgent: Contexto inicial encontrado no DB: {len(all_results)} parágrafos.")

                # Filtra os resultados para conter termos da UFPB
                ufpb_context = [res for res in all_results if any(term.lower() in res.lower() for term in UFPB_TERMS)]

                if ufpb_context:
                    print(f"LLMAgent: Retornando {len(ufpb_context)} parágrafos filtrados por UFPB.")
                    context_list = ufpb_context
                else:
                    print("LLMAgent: Nenhum parágrafo continha termos da UFPB. Usando resultados originais como fallback.")
                    context_list = all_results # Fallback: usa os resultados originais se nenhum mencionar UFPB
            else:
                 print(f"LLMAgent: Nenhum contexto encontrado no DB para a pergunta.")

        except sqlite3.Error as e:
            print(f"LLMAgent: Erro ao consultar DB para contexto: {e}")
            context_list = all_results # Retorna o que foi encontrado antes do erro, se houver
        finally:
            if conn:
                conn.close()
        return context_list

    def _build_prompt(self, pergunta: str, context: Optional[List[str]] = None) -> str:
        """ Monta o prompt para o LLM, focando em UFPB. """
        instruction = "Responda à pergunta." # Instrução base
        context_prefix = ""

        if context:
            context_str = "\n".join([f"- {item}" for item in context])
            context_prefix = f"Contexto:\n{context_str}\n\n"
            instruction = "Responda com base SOMENTE no contexto acima."

        # Adiciona a diretiva sobre UFPB e outras universidades
        ufpb_directive = "A resposta deve considerar apenas informações da Universidade Federal da Paraíba (UFPB), ignorando quaisquer menções a outras universidades."

        # Monta o prompt final
        prompt = f"{context_prefix}Pergunta: {pergunta}\n\n{instruction} {ufpb_directive}"

        # Debug do prompt (opcional)
        # print(f"--- Prompt para LLM ---\n{prompt}\n-----------------------")
        return prompt

    async def responder(self, pergunta: str, context: Optional[List[str]] = None) -> str:
        """ Envia ASYNCRONAMENTE a pergunta para a API Groq e retorna a resposta. """
        print(f"LLMAgent (async Groq): Recebida pergunta: '{pergunta[:50]}...'")

        if context is None:
            print("LLMAgent (async Groq): Contexto não fornecido, buscando/filtrando no DB (sync)...")
            context = self._fetch_context_from_db(pergunta)
            # Se fetch_context_from_db retornar lista vazia, _build_prompt tratará disso

        prompt = self._build_prompt(pergunta, context)

        # --- Monta Payload e Headers para Groq (formato OpenAI) ---
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.5, # Ajuste conforme necessário
            "max_tokens": 1024, # Ajuste conforme necessário
            "top_p": 1,
            "stream": False,
            "stop": None
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        # -------------------------------------------------------------

        try:
            # Usa httpx.AsyncClient para chamada de rede assíncrona
            async with httpx.AsyncClient(timeout=GROQ_TIMEOUT) as client:
                print(f"LLMAgent (async Groq): Enviando requisição para Groq API ({GROQ_API_URL})...")
                response = await client.post(GROQ_API_URL, json=payload, headers=headers)
                response.raise_for_status() # Lança exceção para erros HTTP (4xx ou 5xx)

            response_data = response.json()

            # --- Extrai resposta do formato OpenAI Chat Completions ---
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message")
                if message and message.get("content"):
                    llm_answer = message["content"].strip()
                    print("LLMAgent (async Groq): Resposta recebida da API.")
                    return llm_answer
                else:
                    print("LLMAgent (async Groq): Resposta da API Groq não continha 'content' esperado.")
                    print(f"Resposta recebida: {response_data}") # Log para depuração
                    return "Desculpe, o modelo retornou uma resposta em formato inesperado."
            else:
                print("LLMAgent (async Groq): Resposta da API Groq não continha 'choices' esperado.")
                print(f"Resposta recebida: {response_data}") # Log para depuração
                return "Desculpe, o modelo não retornou nenhuma escolha de resposta."
            # -----------------------------------------------------------

        except httpx.TimeoutException:
            print(f"LLMAgent (async Groq): Erro de Timeout ({GROQ_TIMEOUT}s) ao chamar a API Groq.")
            return "Desculpe, a solicitação ao modelo de linguagem demorou muito para responder."
        except httpx.RequestError as e:
            print(f"LLMAgent (async Groq): Erro de rede ao chamar a API Groq: {e}")
            return "Desculpe, houve um problema de comunicação ao tentar gerar a resposta (rede)."
        except httpx.HTTPStatusError as e:
            # Erro específico HTTP (4xx, 5xx)
            print(f"LLMAgent (async Groq): Erro HTTP {e.response.status_code} ao chamar a API Groq: {e.response.text}")
            if e.response.status_code == 401:
                 return "Desculpe, a chave de API fornecida para o serviço de linguagem é inválida."
            elif e.response.status_code == 429:
                 return "Desculpe, o limite de requisições para o serviço de linguagem foi atingido. Tente novamente mais tarde."
            else:
                 return f"Desculpe, o serviço de linguagem retornou um erro HTTP {e.response.status_code}."
        except json.JSONDecodeError:
            print("LLMAgent (async Groq): Erro ao decodificar JSON da resposta da API Groq.")
            return "Desculpe, recebi uma resposta inválida do serviço de linguagem."
        except Exception as e:
            print(f"LLMAgent (async Groq): Erro inesperado na interação com LLM: {type(e).__name__} - {e}")
            return "Desculpe, ocorreu um erro inesperado ao tentar gerar a resposta."

# Exemplo de uso atualizado para async
async def main_test_llm():
    llm_agent = LLMAgent()
    print("\n--- Teste LLM Async Groq: Pergunta genérica ---")
    pergunta_gen = "Explique o conceito de entropia em termodinâmica."
    resposta_gen = await llm_agent.responder(pergunta_gen)
    print(f"Pergunta: {pergunta_gen}")
    print(f"Resposta LLM: {resposta_gen}")

if __name__ == '__main__':
    asyncio.run(main_test_llm()) 