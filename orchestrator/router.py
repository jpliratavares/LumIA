import sys
import os

# Adiciona o diretório raiz ao sys.path para encontrar o módulo agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.prape_agent import responder_pergunta as responder_prape
# Importar outros agentes aqui quando forem implementados
# from agents.ru_agent import responder_pergunta as responder_ru
# from agents.sigaa_agent import responder_pergunta as responder_sigaa
# from agents.fallback_agent import responder_pergunta as responder_fallback

# Palavras-chave para rotear para o agente PRAPE
KEYWORDS_PRAPE = ["prape", "auxílio", "assistência", "bolsa", "renda", "restaurante", "moradia", "psicológico", "pedagógico"]
# Adicionar keywords para outros agentes conforme necessário


def rotear(pergunta: str) -> str:
    """ Roteia a pergunta para o agente apropriado com base em palavras-chave. """
    pergunta_lower = pergunta.lower()

    # Verifica PRAPE
    if any(keyword in pergunta_lower for keyword in KEYWORDS_PRAPE):
        print("Roteando para o agente PRAPE.")
        return responder_prape(pergunta)

    # Verificar outros agentes aqui...
    # Exemplo:
    # elif any(keyword in pergunta_lower for keyword in KEYWORDS_RU):
    #     print("Roteando para o agente RU.")
    #     return responder_ru(pergunta)
    # elif any(keyword in pergunta_lower for keyword in KEYWORDS_SIGAA):
    #     print("Roteando para o agente SIGAA.")
    #     return responder_sigaa(pergunta)

    # Se nenhum agente especializado for encontrado, usar fallback (ou retornar mensagem genérica)
    else:
        print("Nenhum agente especializado identificado. Usando resposta genérica.")
        # return responder_fallback(pergunta) # Quando o fallback agent for implementado
        return "Desculpe, ainda não consigo responder essa pergunta sobre este tópico específico."

# Exemplo de uso
if __name__ == '__main__':
    pergunta1 = "Como funciona o auxílio moradia da prape?"
    resposta1 = rotear(pergunta1)
    print(f"Pergunta: {pergunta1}\nResposta: {resposta1}\n")

    pergunta2 = "Qual o cardápio do RU hoje?"
    resposta2 = rotear(pergunta2)
    print(f"Pergunta: {pergunta2}\nResposta: {resposta2}\n")

    pergunta3 = "Como fazer matrícula em disciplina?"
    resposta3 = rotear(pergunta3)
    print(f"Pergunta: {pergunta3}\nResposta: {resposta3}\n") 