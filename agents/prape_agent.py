import sys
import os
import sqlite3

# Adiciona o diretório raiz ao sys.path para encontrar o módulo utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.db_handler import create_connection

TABLE_NAME = "prape"

def responder_pergunta(pergunta: str) -> str:
    """ Busca uma resposta no banco de dados para a pergunta dada. """
    conn = create_connection()
    if conn is None:
        return "Desculpe, estou com problemas para acessar minha base de conhecimento no momento."

    resposta_encontrada = None
    try:
        cur = conn.cursor()
        # Busca simplificada usando LIKE em pergunta (se houver) e resposta
        # Adiciona '%' para buscar substrings
        termo_busca = f"%{pergunta}%"
        palavras = pergunta.split()
        for palavra in palavras:
            cur.execute("SELECT resposta FROM prape WHERE resposta LIKE ?", (f"%{palavra}%",))
            resultado = cur.fetchone()
            if resultado:
                resposta_encontrada = resultado[0]
                break
        cur.execute("SELECT resposta FROM prape WHERE resposta LIKE ?", (f"%{pergunta}%",))

        resultado = cur.fetchone()
        if resultado:
            resposta_encontrada = resultado[0]
    except sqlite3.Error as e:
        print(f"Erro ao consultar o banco de dados: {e}")
        # Não retorna o erro técnico para o usuário final
        resposta_encontrada = "Ocorreu um erro ao processar sua pergunta."
    finally:
        if conn:
            conn.close()

    if resposta_encontrada:
        return resposta_encontrada
    else:
        return "Desculpe, não encontrei uma resposta direta para sua pergunta sobre a PRAPE nos meus dados atuais."

# Exemplo de uso (pode ser removido ou comentado)
if __name__ == '__main__':
    # Teste - assumindo que o scraper já rodou e criou/populou o db
    teste_pergunta = "auxílio"
    resposta = responder_pergunta(teste_pergunta)
    print(f"Pergunta: {teste_pergunta}")
    print(f"Resposta: {resposta}")

    teste_pergunta_sem_resposta = "qual a cor do cavalo branco"
    resposta = responder_pergunta(teste_pergunta_sem_resposta)
    print(f"\nPergunta: {teste_pergunta_sem_resposta}")
    print(f"Resposta: {resposta}") 