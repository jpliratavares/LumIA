import sys
import os
from typing import Optional, Dict, Any
import asyncio

# Adiciona o diretório raiz ao sys.path se necessário
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Exemplo: Se precisar do LLMAgent futuramente
# from agents.llm_agent import LLMAgent
# llm_agent = LLMAgent()

class UFPBAgent:
    """
    Agente genérico para responder perguntas sobre a UFPB que não se encaixam 
    nos agentes temáticos específicos (SIGAA, RU, Assistência).

    Escopo: Informações institucionais gerais, estrutura da UFPB, centros, 
            pró-reitorias (visão geral), notícias, eventos, contatos gerais.
    Fonte Esperada: Banco de dados com conteúdo geral do site www.ufpb.br 
                    (excluindo as áreas já cobertas pelos outros agentes).
    """

    async def responder_pergunta(self, pergunta: str) -> Optional[Dict[str, Any]]:
        """ Tenta responder a pergunta geral sobre a UFPB. (Não implementado) """
        print(f"UFPBAgent: Recebida pergunta (não implementado): '{pergunta[:50]}...'")
        # logs = [f"UFPBAgent: Recebida pergunta: '{pergunta[:50]}...'"]

        # TODO: Implementar lógica de busca contextual na tabela geral do site
        # Ex: buscar em `ufpb_content` (ou na tabela `prape` se tudo foi salvo lá)

        # TODO: Se encontrar info, refinar com LLM? (llm_agent.responder)

        # TODO: Retornar dicionário com 'answer', 'raw_answer', 'logs' ou None

        return None  # Retorna None indicando que não pode responder ainda

# Exemplo de uso (para teste futuro)
# async def main_test_ufpb():
#     agent = UFPBAgent()
#     pergunta = "Quais são os centros de ensino da UFPB?"
#     resposta = await agent.responder_pergunta(pergunta)
#     print(f"Pergunta: {pergunta}")
#     print(f"Resposta: {resposta}")
# 
# if __name__ == '__main__':
#     asyncio.run(main_test_ufpb()) 