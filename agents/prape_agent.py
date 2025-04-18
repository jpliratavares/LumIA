import sys
import os
import aiosqlite # Importa aiosqlite
import asyncio # Necessário para o exemplo e async
import sqlite3
from typing import List, Optional, Dict, Any

# Adiciona o diretório raiz ao sys.path para encontrar os módulos utils e agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# utils.db_handler usa sqlite3, precisamos do path direto ou adaptar db_handler
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db')
DB_PATH = os.path.join(DB_DIR, 'lumia.db')

# from utils.db_handler import create_connection, create_table # Não usaremos create_connection síncrono
from agents.llm_agent import LLMAgent # Usaremos SEMPRE que achar algo no DB

TABLE_NAME = "prape"

# Instancia o LLM Agent (pode ser singleton)
llm_agent = LLMAgent()

async def _buscar_resposta_direta(pergunta: str) -> Optional[str]:
    """ Tenta encontrar ASYNCRONAMENTE UMA resposta relevante no banco de dados. """
    resposta = None
    try:
        # Conecta usando aiosqlite
        async with aiosqlite.connect(DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row # Para acessar colunas por nome (opcional)
            termo_busca = f"%{pergunta}%"
            # Executa a busca async
            async with conn.execute(f"SELECT resposta FROM {TABLE_NAME} WHERE resposta LIKE ? LIMIT 1", (termo_busca,)) as cursor:
                resultado = await cursor.fetchone()
                if resultado:
                    resposta = resultado["resposta"]
                else:
                    # Tenta busca por palavras-chave
                    palavras = [p for p in pergunta.split() if len(p) > 3]
                    if palavras:
                        like_clauses = " OR ".join(["resposta LIKE ?"] * len(palavras))
                        params = [f"%{p}%" for p in palavras]
                        async with conn.execute(f"SELECT resposta FROM {TABLE_NAME} WHERE {like_clauses} LIMIT 1", params) as cursor_kw:
                            resultado_kw = await cursor_kw.fetchone()
                            if resultado_kw:
                                resposta = resultado_kw["resposta"]
    except aiosqlite.Error as e:
        print(f"PRAEAgent (async): Erro ao buscar resposta direta: {e}")
    except Exception as e_generic:
         print(f"PRAEAgent (async): Erro genérico inesperado na busca DB: {e_generic}")
    return resposta

async def responder_pergunta(pergunta: str) -> Optional[Dict[str, Any]]:
    """ Busca ASYNCRONAMENTE uma resposta no DB. Se encontrar, refina com LLM e retorna dict. Se não encontrar, retorna None. """
    logs = [f"PRAEAgent (async): Recebida pergunta: '{pergunta[:50]}...'"]
    print(logs[-1])

    raw_answer_db = None
    final_answer = None

    try:
        # 1. Tenta buscar UMA resposta direta no DB (agora async)
        logs.append("PRAEAgent (async): Buscando resposta direta no DB...")
        print(logs[-1])
        raw_answer_db = await _buscar_resposta_direta(pergunta)

        if raw_answer_db:
            logs.append(f"PRAEAgent (async): Resposta encontrada no DB (primeiros 50 chars): {raw_answer_db[:50]}...")
            print(logs[-1])
            logs.append("PRAEAgent (async): Refinando resposta com LLM...")
            print(logs[-1])
            # 2. Se encontrou, SEMPRE envia para o LLM refinar (LLM agora é async)
            final_answer = await llm_agent.responder(pergunta, context=[raw_answer_db])
            logs.append(f"PRAEAgent (async): Resposta refinada recebida do LLM (ou erro do LLM).")
            print(logs[-1])
        else:
            # 3. Nenhuma resposta encontrada no DB
            logs.append("PRAEAgent (async): Nenhuma resposta encontrada no DB.")
            print(logs[-1])
            final_answer = None # Sinaliza para o orquestrador

    except Exception as e:
        logs.append(f"PRAEAgent (async): Erro inesperado: {e}")
        print(logs[-1])
        # Retorna um dict de erro em vez de None para fornecer info
        final_answer = "Desculpe, ocorreu um erro inesperado ao processar sua pergunta sobre a PRAPE."

    # Monta o dicionário de resultado
    if final_answer is None and raw_answer_db is None:
        print("PRAEAgent (async): Retornando None (nenhuma info encontrada).")
        return None
    else:
        result_dict = {
            "answer": final_answer if final_answer else "Não foi possível gerar uma resposta final.",
            "raw_answer": raw_answer_db,
            "logs": logs
        }
        print(f"PRAEAgent (async): Retornando dicionário: { {k: v if k != 'logs' else f'{len(v)} logs' for k, v in result_dict.items()} }")
        return result_dict

# Exemplo de uso atualizado para async
async def main_test_prape():
    # --- Configurar DB (Síncrono, apenas para teste) ---
    try:
        # Usando sqlite3 síncrono só para popular o DB para o teste
        conn_sync = sqlite3.connect(DB_PATH)
        conn_sync.execute(""" CREATE TABLE IF NOT EXISTS prape (
                                            id integer PRIMARY KEY,
                                            pergunta text, 
                                            resposta text NOT NULL UNIQUE
                                        ); """)
        test_data = [
            ("Auxílios", "Fixa os Valores dos Auxílios Estudantis da Pró-Reitoria de Assistência e Promoção ao Estudante"), 
            ("Auxílio Alimentação", "O Auxílio Alimentação destina-se a cobrir parte das despesas com refeições dos estudantes em vulnerabilidade socioeconômica comprovada. O valor atual é X."), 
            ("Documentos Moradia", "Para o auxílio moradia, precisa de RG, CPF, comprovante de matrícula, histórico, comprovante de residência familiar e declaração de aluguel."), 
            ("Contato PRAE", "Contato: email@exemplo.com, telefone (XX) XXXX-XXXX.") 
        ]
        for q, r in test_data:
            try:
                conn_sync.execute("INSERT INTO prape(pergunta, resposta) VALUES (?, ?)", (q, r))
            except sqlite3.IntegrityError:
                pass
        conn_sync.commit()
        conn_sync.close()
    except Exception as db_setup_e:
        print(f"Erro configurando DB para teste: {db_setup_e}")
    # -----------------------------------------------------

    # Teste 1: Pergunta com resposta direta no DB (será refinada)
    pergunta_com_db = "Como funciona o Auxílio Alimentação?"
    print(f"\n--- Teste DB -> LLM ({pergunta_com_db}) ---")
    resposta_com_db = await responder_pergunta(pergunta_com_db)
    print(f"Resultado Final Dict: {resposta_com_db}") 

    # Teste 2: Pergunta com resposta direta CURTA no DB (será refinada)
    pergunta_curta = "Qual o contato da PRAE?"
    print(f"\n--- Teste DB Curta -> LLM ({pergunta_curta}) ---")
    resposta_curta = await responder_pergunta(pergunta_curta)
    print(f"Resultado Final Dict: {resposta_curta}")

    # Teste 3: Pergunta sem resposta direta no DB
    pergunta_sem_db = "Como funciona o empréstimo de livros na biblioteca?"
    print(f"\n--- Teste Sem DB ({pergunta_sem_db}) ---")
    resposta_sem_db = await responder_pergunta(pergunta_sem_db)
    print(f"Resultado Final: {resposta_sem_db}") # Espera-se None

if __name__ == '__main__':
    asyncio.run(main_test_prape()) 