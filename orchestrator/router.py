import sys
import os
from typing import Dict, Any, Optional # Adicionar tipos

# Adiciona o diretório raiz ao sys.path para encontrar o módulo agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.prape_agent import responder_pergunta as responder_prape
# Importar outros agentes aqui quando forem implementados
# from agents.ru_agent import responder_pergunta as responder_ru
# from agents.sigaa_agent import responder_pergunta as responder_sigaa
# from agents.fallback_agent import responder_pergunta as responder_fallback
from agents.llm_agent import LLMAgent # Importa o LLM Agent para fallback geral

# Palavras-chave para rotear para o agente PRAPE
KEYWORDS_PRAPE = ["prape", "auxílio", "assistência", "bolsa", "renda", "restaurante", "moradia", "psicológico", "pedagógico"]
# Adicionar keywords para outros agentes conforme necessário

# --- Instâncias dos Agentes ---
llm_agent = LLMAgent() # Instancia o LLM Agent para fallback

async def rotear(pergunta: str) -> Optional[Dict[str, Any]]: # Atualiza tipo de retorno
    """ Roteia a pergunta para o agente apropriado ou usa LLM como fallback, retornando um dict. """
    pergunta_lower = pergunta.lower()
    print(f"Orchestrator: Roteando pergunta: '{pergunta[:50]}...'")

    # 1. Tenta rotear para Agentes Temáticos
    if any(keyword in pergunta_lower for keyword in KEYWORDS_PRAPE):
        print("Orchestrator: Roteando para Agente PRAPE.")
        # PrapeAgent já retorna Dict ou None
        resultado_agente = await responder_prape(pergunta)
        if resultado_agente: # Se retornou um dict
            return resultado_agente
        else: # Se retornou None (não achou nada no DB)
            print("Orchestrator: Agente PRAPE não encontrou dados. Usando LLM fallback.")
            # Prossegue para o fallback LLM abaixo
            pass # Apenas para clareza

    # Verificar outros agentes aqui...
    # Exemplo:
    # elif any(keyword in pergunta_lower for keyword in KEYWORDS_RU):
    #     print("Roteando para o agente RU.")
    #     return responder_ru(pergunta)
    # elif any(keyword in pergunta_lower for keyword in KEYWORDS_SIGAA):
    #     print("Roteando para o agente SIGAA.")
    #     return responder_sigaa(pergunta)

    # 2. Se nenhum agente temático correspondeu OU agente temático retornou None
    print("Orchestrator: Usando LLM Agent como fallback geral.")
    # Chama o LLM sem contexto específico
    resposta_fallback_str = await llm_agent.responder(pergunta)
    # Envolve a resposta string do LLM em um dict para consistência
    return {
        "answer": resposta_fallback_str,
        "raw_answer": None,
        "logs": ["Orchestrator: Roteado para LLM fallback geral."]
    }

# Exemplo de uso
async def main_test(): # Transforma em async para testar
    pergunta_prape = "Como funciona o auxílio moradia da prape?"
    print(f"\n--- Teste Roteamento PRAPE ({pergunta_prape}) ---")
    resposta_prape = await rotear(pergunta_prape)
    print(f"Resultado Final Dict: {resposta_prape}")

    pergunta_generica = "Qual a capital da França?"
    print(f"\n--- Teste Roteamento Fallback ({pergunta_generica}) ---")
    resposta_generica = await rotear(pergunta_generica)
    print(f"Resultado Final Dict: {resposta_generica}")

    # Adicionar testes para outros agentes quando implementados
    # pergunta_ru = "Qual o cardápio do RU hoje?"
    # print(f"\n--- Teste Roteamento RU ({pergunta_ru}) ---")
    # resposta_ru = rotear(pergunta_ru)
    # print(f"Resposta Final: {resposta_ru}")

    pergunta3 = "Como fazer matrícula em disciplina?"
    resposta3 = await rotear(pergunta3)
    print(f"Pergunta: {pergunta3}\nResposta: {resposta3}\n")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main_test()) # Executa o teste async 