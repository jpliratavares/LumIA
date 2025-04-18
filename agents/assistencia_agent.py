import sys
import os
from typing import Optional, Dict, Any
import asyncio

# Adiciona o diretório raiz ao sys.path se necessário
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Exemplo: Se precisar do LLMAgent futuramente
# from agents.llm_agent import LLMAgent
# llm_agent = LLMAgent()

class AssistenciaAgent:
    """
    Agente focado em responder sobre diversos programas de Assistência Estudantil 
    da UFPB (complementar ou talvez substituir o PRAPE Agent dependendo da granularidade).

    Escopo: Auxílios (moradia, alimentação, creche, transporte, etc.), bolsas 
            (permanência, Pibic, Pibex), apoio psicológico/pedagógico, editais 
            de assistência.
    Fonte Esperada: Banco de dados com informações da PRAPE e outras pró-reitorias 
                    relevantes (PRG, PRPG, Proex).
    """

    async def responder_pergunta(self, pergunta: str) -> Optional[Dict[str, Any]]:
        """ Tenta responder a pergunta sobre Assistência Estudantil. (Não implementado) """
        print(f"AssistenciaAgent: Recebida pergunta (não implementado): '{pergunta[:50]}...'")
        # logs = [f"AssistenciaAgent: Recebida pergunta: '{pergunta[:50]}...'"]

        # TODO: Implementar lógica de busca contextual em tabelas de auxílios, bolsas, editais
        # Ex: buscar em `auxilios`, `bolsas`, `editais_assistencia`

        # TODO: Se encontrar info, refinar com LLM? (llm_agent.responder)

        # TODO: Retornar dicionário com 'answer', 'raw_answer', 'logs' ou None

        return None  # Retorna None indicando que não pode responder ainda

# Exemplo de uso (para teste futuro)
# async def main_test_assistencia():
#     agent = AssistenciaAgent()
#     pergunta = "Quais são os tipos de bolsa disponíveis?"
#     resposta = await agent.responder_pergunta(pergunta)
#     print(f"Pergunta: {pergunta}")
#     print(f"Resposta: {resposta}")
# 
# if __name__ == '__main__':
#     asyncio.run(main_test_assistencia()) 