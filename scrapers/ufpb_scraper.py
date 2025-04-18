import requests
from bs4 import BeautifulSoup
import sys
import os

# Adiciona o diretório pai ao sys.path para encontrar o módulo utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.db_handler import create_connection, create_table, insert_data

URL = "https://www.ufpb.br/prape"
TABLE_NAME = "prape"

def fetch_page_content(url):
    """ Busca o conteúdo HTML da URL fornecida. """
    try:
        response = requests.get(url)
        response.raise_for_status() # Verifica se houve erro HTTP
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a URL {url}: {e}")
        return None

def extract_paragraphs(html_content):
    """ Extrai todos os parágrafos (<p>) do conteúdo HTML. """
    if html_content is None:
        return []
    soup = BeautifulSoup(html_content, 'html.parser')
    # Tenta encontrar o conteúdo principal para refinar a busca
    # Isso pode precisar de ajuste dependendo da estrutura do site
    # Exemplo: content_div = soup.find('div', id='content') or soup.find('main')
    # Se encontrar, busca parágrafos dentro dele: paragraphs = content_div.find_all('p')
    # Caso contrário, busca em todo o body:
    paragraphs = soup.find_all('p')
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

def main():
    print(f"Iniciando scraping da URL: {URL}")
    html_content = fetch_page_content(URL)

    if not html_content:
        print("Não foi possível obter o conteúdo da página. Encerrando.")
        return

    paragraphs = extract_paragraphs(html_content)
    print(f"Encontrados {len(paragraphs)} parágrafos.")

    if not paragraphs:
        print("Nenhum parágrafo encontrado para inserir no banco de dados.")
        return

    conn = create_connection()
    if conn is None:
        print("Não foi possível conectar ao banco de dados. Encerrando.")
        return

    # Cria a tabela se não existir
    sql_create_prape_table = f""" CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                        id integer PRIMARY KEY,
                                        pergunta text, -- Pode ser preenchido posteriormente ou adaptado
                                        resposta text NOT NULL
                                    ); """
    create_table(conn, sql_create_prape_table)

    print(f"Inserindo dados na tabela '{TABLE_NAME}'...")
    count = 0
    for para_text in paragraphs:
        # Simplesmente insere o parágrafo como 'resposta', 'pergunta' fica vazia
        # Pode ser adaptado para extrair perguntas de títulos anteriores, etc.
        insert_id = insert_data(conn, TABLE_NAME, None, para_text)
        if insert_id:
            count += 1
        else:
            print(f"Falha ao inserir parágrafo: {para_text[:50]}...")

    print(f"{count} registros inseridos com sucesso na tabela '{TABLE_NAME}'.")
    conn.close()
    print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main() 