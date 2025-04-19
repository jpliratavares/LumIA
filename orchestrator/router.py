import sys
import os
from typing import Dict, Any, Optional

# Adiciona o diretório raiz ao sys.path para encontrar o módulo agents
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# --- Importa Agentes --- #
from agents.prape_agent import responder_pergunta as responder_prape
from agents.sigaa_agent import SIGAAAgent
from agents.ru_agent import RUAgent
from agents.assistencia_agent import AssistenciaAgent
from agents.ufpb_agent import UFPBAgent
from agents.llm_agent import LLMAgent # Fallback geral

# --- Palavras-chave para Roteamento --- #
# Ajustar e refinar estas listas é crucial para o bom funcionamento
KEYWORDS_PRAPE = [
    "prape", "moradia", "psicológico", "pedagógico", # Termos mais específicos da PRAPE
    "restaurante universitário" # RU pode estar sob PRAPE?
]
KEYWORDS_ASSISTENCIA = [
    "assistência", "auxílio", "bolsa", "renda", "alimentação", "creche",
    "transporte", "permanência", "pnaes", "vulnerabilidade", "socioeconômica"
]
KEYWORDS_SIGAA = [
    "sigaa", "matrícula", "disciplina", "histórico", "nota", "trancamento",
    "atestado", "declaração", "documento acadêmico", "cra", "período letivo",
    "ira", "portal discente"
]
KEYWORDS_RU = [
    "ru", "restaurante universitário", "cardápio", "refeição", "créditos ru",
    "bandejão", "preço ru", "horário ru"
]
KEYWORDS_UFPB = [ # Palavras gerais, menos específicas
    "ufpb", "universidade federal da paraíba", "reitoria", "pró-reitoria",
    "campus", "centro de ensino", "biblioteca", "departamento", "curso",
    "contato", "endereço", "notícia", "evento", "calendário acadêmico"
]

# --- Instâncias dos Agentes --- #
# É importante instanciar apenas uma vez se não tiverem estado interno complexo
sigaa_agent = SIGAAAgent()
ru_agent = RUAgent()
assistencia_agent = AssistenciaAgent()
ufpb_agent = UFPBAgent()
llm_agent = LLMAgent()

async def rotear(pergunta: str) -> Optional[Dict[str, Any]]:
    """ Roteia a pergunta para o agente temático apropriado ou usa LLM como fallback. """
    pergunta_lower = pergunta.lower()
    print(f"Orchestrator: Roteando pergunta: '{pergunta[:50]}...'")

    # --- 🔍 Interceptação especial: Identidade da IA --- #
    if any(x in pergunta_lower for x in ["qual seu nome", "teu nome", "seu nome", "quem é você", "quem é voce"]):
        print("Orchestrator: Resposta direta para identidade da IA.")
        return {
            "answer": "Meu nome é LumIA! Sou a assistente inteligente da Universidade Federal da Paraíba (UFPB), criada para te ajudar com dúvidas acadêmicas, auxílios, notas e muito mais 🤖📚",
            "raw_answer": None,
            "logs": ["Resposta direta para pergunta sobre identidade da LumIA."]
        }


    # --- Roteamento por Palavras-chave --- #
    # A ordem aqui pode ser importante dependendo do overlap das keywords

    # 1. SIGAA (Sistema Acadêmico)
    if any(keyword in pergunta_lower for keyword in KEYWORDS_SIGAA):
        print("Orchestrator: Roteando para Agente SIGAA.")
        resultado_agente = await sigaa_agent.responder_pergunta(pergunta)
        if resultado_agente:
            return resultado_agente
        else:
            print("Orchestrator: Agente SIGAA não encontrou resposta. Prosseguindo...")

    # 2. RU (Restaurante Universitário)
    # Verificar RU antes de PRAPE/Assistencia se "restaurante universitário" estiver em ambos
    if any(keyword in pergunta_lower for keyword in KEYWORDS_RU):
        print("Orchestrator: Roteando para Agente RU.")
        resultado_agente = await ru_agent.responder_pergunta(pergunta)
        if resultado_agente:
            return resultado_agente
        else:
            print("Orchestrator: Agente RU não encontrou resposta. Prosseguindo...")

    # 3. Assistência Estudantil (Auxílios, Bolsas, etc.)
    # Verificar Assistencia antes de PRAPE se houver overlap
    if any(keyword in pergunta_lower for keyword in KEYWORDS_ASSISTENCIA):
        print("Orchestrator: Roteando para Agente Assistencia.")
        resultado_agente = await assistencia_agent.responder_pergunta(pergunta)
        if resultado_agente:
            return resultado_agente
        else:
            print("Orchestrator: Agente Assistencia não encontrou resposta. Prosseguindo...")

    # 4. PRAPE (Estrutura/Serviços específicos da PRAPE não cobertos por Assistencia)
    if any(keyword in pergunta_lower for keyword in KEYWORDS_PRAPE):
        print("Orchestrator: Roteando para Agente PRAPE.")
        resultado_agente = await responder_prape(pergunta) # Usa a função importada
        if resultado_agente:
            return resultado_agente
        else:
            print("Orchestrator: Agente PRAPE não encontrou resposta. Prosseguindo...")

    # 5. UFPB Geral (Informações institucionais, etc.)
    if any(keyword in pergunta_lower for keyword in KEYWORDS_UFPB):
        print("Orchestrator: Roteando para Agente UFPB Geral.")
        resultado_agente = await ufpb_agent.responder_pergunta(pergunta)
        if resultado_agente:
            return resultado_agente
        else:
            print("Orchestrator: Agente UFPB Geral não encontrou resposta. Usando LLM fallback.")

    # 6. Fallback Geral com LLM
    print("Orchestrator: Nenhum agente temático respondeu. Usando LLM Agent como fallback geral.")
    resposta_fallback_str = await llm_agent.responder(pergunta)
    # Envolve a resposta string do LLM em um dict para consistência
    return {
        "answer": resposta_fallback_str,
        "raw_answer": None,
        "logs": ["Orchestrator: Roteado para LLM fallback geral."]
    }

# Exemplo de uso atualizado com novos agentes
async def main_test():
    perguntas_teste = {
        "SIGAA": "Como faço para trancar uma disciplina no SIGAA?",
        "RU": "Qual o preço da refeição no RU?",
        "Assistencia": "Como solicitar auxílio transporte?",
        "PRAPE": "Qual o contato da PRAPE?", # Pode cair em PRAPE ou Assistencia dependendo das keywords
        "UFPB": "Qual o endereço do campus IV?",
        "Fallback": "Me fale sobre a história do Brasil."
    }

    for agente, pergunta in perguntas_teste.items():
        print(f"\n--- Teste Roteamento {agente} ({pergunta}) ---")
        resultado = await rotear(pergunta)
        # Imprime de forma mais legível
        if resultado:
            print(f"  Answer: {resultado.get('answer')[:100]}...")
            print(f"  Raw Answer: {str(resultado.get('raw_answer'))[:100]}...")
            print(f"  Logs: {len(resultado.get('logs', []))} entradas")
            # print(f"  Full Logs: {resultado.get('logs')}") # Descomentar para ver logs completos
        else:
            print("  Resultado: None")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main_test()) 