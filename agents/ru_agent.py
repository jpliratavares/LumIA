import sys
import os
from typing import Optional, Dict, Any
import asyncio

# Adiciona o diretório raiz ao sys.path se necessário
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Exemplo: Se precisar do LLMAgent futuramente
# from agents.llm_agent import LLMAgent
# llm_agent = LLMAgent()

class RUAgent:
    """
    Agente especializado em responder perguntas sobre o Restaurante Universitário (RU) 
    da UFPB.

    Escopo: Cardápio do dia/semana, horários de funcionamento, localização,
            preços, regras de acesso, compra de créditos.
    Fonte Esperada: Banco de dados com informações do site/sistema do RU, 
                    ou API específica do RU.
    """

    async def responder_pergunta(self, pergunta: str) -> Optional[Dict[str, Any]]:
        """ Tenta responder a pergunta sobre o RU. (Não implementado) """
        print(f"RUAgent: Recebida pergunta (não implementado): '{pergunta[:50]}...'")
        # logs = [f"RUAgent: Recebida pergunta: '{pergunta[:50]}...'"]

        # TODO: Implementar lógica de busca contextual específica do RU
        # Ex: buscar cardápio na tabela `ru_cardapio`, verificar horários em `ru_info`

        # TODO: Se encontrar info, refinar com LLM? (llm_agent.responder)

        # TODO: Retornar dicionário com 'answer', 'raw_answer', 'logs' ou None

        return None  # Retorna None indicando que não pode responder ainda

# Exemplo de uso (para teste futuro)
# async def main_test_ru():
#     agent = RUAgent()
#     pergunta = "Qual o cardápio do RU hoje?"
#     resposta = await agent.responder_pergunta(pergunta)
#     print(f"Pergunta: {pergunta}")
#     print(f"Resposta: {resposta}")
# 
# if __name__ == '__main__':
#     asyncio.run(main_test_ru()) 