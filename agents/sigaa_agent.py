import sys
import os
from typing import Optional, Dict, Any
import asyncio # Pode ser útil para futuras implementações async

# Adiciona o diretório raiz ao sys.path se necessário para futuros imports
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Exemplo: Se precisar do LLMAgent futuramente
# from agents.llm_agent import LLMAgent
# llm_agent = LLMAgent()

class SIGAAAgent:
    """ 
    Agente especializado em responder perguntas sobre o SIGAA (Sistema Integrado de Gestão 
    de Atividades Acadêmicas) da UFPB.

    Escopo: Matrícula, disciplinas, notas, histórico, trancamento, atestados, 
            documentos acadêmicos via SIGAA.
    Fonte Esperada: Banco de dados com informações extraídas do SIGAA (ou API futura).
    """

    async def responder_pergunta(self, pergunta: str) -> Optional[Dict[str, Any]]:
        """ Tenta responder a pergunta sobre o SIGAA. (Não implementado) """
        print(f"SIGAAAgent: Recebida pergunta (não implementado): '{pergunta[:50]}...'")
        # logs = [f"SIGAAAgent: Recebida pergunta: '{pergunta[:50]}...'"]

        # TODO: Implementar lógica de busca contextual específica do SIGAA
        # Ex: buscar em tabela `sigaa_content`, chamar API do SIGAA se existir

        # TODO: Se encontrar info, refinar com LLM? (llm_agent.responder)

        # TODO: Retornar dicionário com 'answer', 'raw_answer', 'logs' ou None

        return None  # Retorna None indicando que não pode responder ainda

# Exemplo de uso (para teste futuro)
# async def main_test_sigaa():
#     agent = SIGAAAgent()
#     pergunta = "Como fazer matrícula em disciplina?"
#     resposta = await agent.responder_pergunta(pergunta)
#     print(f"Pergunta: {pergunta}")
#     print(f"Resposta: {resposta}")
# 
# if __name__ == '__main__':
#     asyncio.run(main_test_sigaa()) 