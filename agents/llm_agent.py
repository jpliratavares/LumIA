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

# Usa o nome do serviço 'ollama' definido no docker-compose.yml para comunicação inter-container
OLLAMA_API_URL = "http://ollama:11434/api/generate"
DEFAULT_MODEL = "mistral"
DB_TABLE_FOR_CONTEXT = "prape"  # Tabela padrão para buscar contexto se não for fornecido
CONTEXT_LIMIT = 3
OLLAMA_TIMEOUT = 300.0 # Timeout aumentado para 300 segundos (5 minutos)

class LLMAgent:
    """ Agente para interagir com um Large Language Model via API Ollama (Async). """

    def _fetch_context_from_db(self, pergunta: str) -> List[str]:
        """ Busca contexto relevante no banco de dados (tabela prape). """
        context_list = []
        conn = create_connection()
        if conn is None:
            print("LLMAgent: Falha ao conectar ao DB para buscar contexto.")
            return context_list

        try:
            cur = conn.cursor()
            termo_busca = f"%{pergunta}%"
            # Busca simples usando LIKE na pergunta e resposta
            # Idealmente, isso usaria uma busca vetorial ou FTS mais avançada
            cur.execute(f"SELECT resposta FROM {DB_TABLE_FOR_CONTEXT} WHERE pergunta LIKE ? OR resposta LIKE ? LIMIT ?",
                        (termo_busca, termo_busca, CONTEXT_LIMIT))
            resultados = cur.fetchall()
            if resultados:
                context_list = [row[0] for row in resultados]
                print(f"LLMAgent: Contexto encontrado no DB: {len(context_list)} parágrafos.")
        except sqlite3.Error as e:
            print(f"LLMAgent: Erro ao consultar DB para contexto: {e}")
        finally:
            if conn:
                conn.close()
        return context_list

    def _build_prompt(self, pergunta: str, context: Optional[List[str]] = None) -> str:
        """ Monta o prompt para o LLM. """
        if context:
            context_str = "\n".join([f"- {item}" for item in context])
            prompt = f"Contexto:\n{context_str}\n\nPergunta: {pergunta}\nResponda com base SOMENTE no contexto acima."
        else:
            # Se nenhum contexto foi fornecido ou encontrado, faz uma pergunta direta
            prompt = f"Pergunta: {pergunta}\nResponda à pergunta."
            print("LLMAgent: Nenhum contexto fornecido ou encontrado, enviando pergunta direta.")

        # print(f"--- Prompt para LLM ---\n{prompt}\n-----------------------") # Debug
        return prompt

    async def responder(self, pergunta: str, context: Optional[List[str]] = None) -> str:
        """ Envia ASYNCRONAMENTE a pergunta para o LLM e retorna a resposta. """
        print(f"LLMAgent (async): Recebida pergunta: '{pergunta[:50]}...'")

        if context is None:
            print("LLMAgent (async): Contexto não fornecido, buscando no DB (sync)...")
            context = self._fetch_context_from_db(pergunta)
            # Se fetch_context_from_db retornar lista vazia, _build_prompt tratará disso

        prompt = self._build_prompt(pergunta, context)

        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }

        try:
            # Usa httpx.AsyncClient para chamada de rede assíncrona
            async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
                print(f"LLMAgent (async): Enviando requisição para Ollama API ({OLLAMA_API_URL}) com prompt: {prompt[:100]}...")
                response = await client.post(OLLAMA_API_URL, json=payload)
                response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)

            response_data = response.json()
            llm_answer = response_data.get("response", "").strip()

            if llm_answer:
                print("LLMAgent (async): Resposta recebida da API.")
                # print(f"--- Resposta LLM ---\n{llm_answer}\n--------------------") # Debug
                return llm_answer
            else:
                print("LLMAgent (async): API Ollama retornou uma resposta vazia.")
                return "Desculpe, o modelo não conseguiu gerar uma resposta válida."

        except httpx.TimeoutException:
            print(f"LLMAgent (async): Erro de Timeout ({OLLAMA_TIMEOUT}s) ao chamar a API Ollama.")
            return "Desculpe, a solicitação ao modelo de linguagem demorou muito para responder."
        except httpx.RequestError as e:
            print(f"LLMAgent (async): Erro ao chamar a API Ollama: {e}")
            # httpx não tem ConnectionError separado como requests, RequestError é mais genérico
            # Poderia checar e.request.url para ver se é erro de conexão
            if "Failed to establish a new connection" in str(e) or "Name or service not known" in str(e):
                 return "Desculpe, não consegui conectar ao serviço de linguagem (Ollama). Verifique se ele está rodando e acessível."
            return "Desculpe, houve um problema de comunicação ao tentar gerar a resposta."
        except json.JSONDecodeError:
            print("LLMAgent (async): Erro ao decodificar JSON da resposta da API Ollama.")
            return "Desculpe, recebi uma resposta inválida do serviço de linguagem."
        except Exception as e:
            print(f"LLMAgent (async): Erro inesperado na interação com LLM: {e}")
            return "Desculpe, ocorreu um erro inesperado ao tentar gerar a resposta."

# Exemplo de uso atualizado para async
async def main_test_llm():
    llm_agent = LLMAgent()
    print("\n--- Teste LLM Async: Pergunta genérica ---")
    pergunta_gen = "Explique o conceito de entropia em termodinâmica."
    resposta_gen = await llm_agent.responder(pergunta_gen)
    print(f"Pergunta: {pergunta_gen}")
    print(f"Resposta LLM: {resposta_gen}")

if __name__ == '__main__':
    # O código de teste original aqui era síncrono e chamava o método responder síncrono.
    # Agora, para testar o método async, precisamos de um loop de eventos.
    # Removendo os testes antigos que não funcionarão mais diretamente.
    asyncio.run(main_test_llm()) 