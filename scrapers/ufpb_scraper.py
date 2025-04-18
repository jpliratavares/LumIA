import requests
from bs4 import BeautifulSoup
import sys
import os
import sqlite3
from urllib.parse import urljoin, urlparse

# Adiciona o diretório pai ao sys.path para encontrar o módulo utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.db_handler import create_connection, create_table, insert_data

BASE_URL = "https://www.ufpb.br/prape"
TABLE_NAME = "prape"
KEYWORDS_LINKS = ["auxilio", "bolsa", "renda", "edital", "moradia", "restaurante", "assistencia"]
IGNORE_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".css", ".js", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]

visited_links = set()

def fetch_page_content(url):
    """ Busca o conteúdo HTML da URL fornecida. """
    global visited_links
    if url in visited_links:
        print(f"-- URL já visitada: {url}")
        return None
    visited_links.add(url)
    print(f"Acessando: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Verifica o content-type para evitar processar não-HTML
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(f"-- Conteúdo não é HTML: {url}")
            return None
        return response.text
    except requests.exceptions.Timeout:
        print(f"Erro de Timeout ao buscar a URL {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar a URL {url}: {e}")
        return None

def is_relevant_link(url, base_url):
    """ Verifica se um link é relevante para o scraping. """
    parsed_url = urlparse(url)
    # Ignora links externos, âncoras, javascript, mailto, etc.
    if not parsed_url.scheme in ['http', 'https'] or parsed_url.netloc != urlparse(base_url).netloc:
        return False
    # Ignora extensões de arquivo
    if any(url.lower().endswith(ext) for ext in IGNORE_EXTENSIONS):
        return False
    # Verifica se começa com a base ou contém keywords
    if url.startswith(base_url):
        return True
    if any(keyword in url.lower() for keyword in KEYWORDS_LINKS):
        return True
    return False

def extract_links(html_content, base_url):
    """ Extrai links relevantes do conteúdo HTML. """
    links = set()
    if html_content is None:
        return links
    soup = BeautifulSoup(html_content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href'].strip()
        # Constrói URL absoluta
        absolute_url = urljoin(base_url, href)
        # Normaliza removendo a âncora
        absolute_url = urlparse(absolute_url)._replace(fragment='').geturl()
        if is_relevant_link(absolute_url, base_url):
            links.add(absolute_url)
    return links

def extract_title_and_paragraphs(html_content):
    """ Extrai o título (title ou h1) e parágrafos (<p>) do HTML. """
    title = "Título não encontrado"
    paragraphs = []
    if html_content is None:
        return title, paragraphs

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extrai título
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        title = title_tag.string.strip()
    else:
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.string:
            title = h1_tag.string.strip()
        else: # Tenta h2 se h1 não for encontrado
            h2_tag = soup.find('h2')
            if h2_tag and h2_tag.string:
                title = h2_tag.string.strip()

    # Extrai parágrafos (pode precisar de ajuste para buscar dentro de divs específicas)
    # Ex: content_div = soup.find('div', id='content') or soup.find('main')
    # if content_div:
    #     paragraphs_tags = content_div.find_all('p')
    # else:
    #     paragraphs_tags = soup.find_all('p')
    paragraphs_tags = soup.find_all('p')
    paragraphs = [p.get_text(strip=True) for p in paragraphs_tags if p.get_text(strip=True)]

    return title, paragraphs

def check_if_exists(conn, table, resposta):
    """ Verifica se um registro com a mesma resposta já existe na tabela. """
    sql = f''' SELECT 1 FROM {table} WHERE resposta = ? LIMIT 1 '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (resposta,))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Erro ao verificar existência na tabela {table}: {e}")
        return False # Assume que não existe em caso de erro para tentar inserir

def main():
    print(f"Iniciando scraping recursivo a partir de: {BASE_URL}")
    links_to_visit = {BASE_URL}
    processed_links = 0

    conn = create_connection()
    if conn is None:
        print("Não foi possível conectar ao banco de dados. Encerrando.")
        return

    # Garante que a tabela existe
    sql_create_prape_table = f""" CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                        id integer PRIMARY KEY,
                                        pergunta text, -- Título da página
                                        resposta text NOT NULL,
                                        UNIQUE(resposta) -- Garante unicidade na resposta
                                    ); """
    create_table(conn, sql_create_prape_table)

    inserted_count_total = 0

    while links_to_visit:
        current_url = links_to_visit.pop()
        if current_url in visited_links:
            continue

        html_content = fetch_page_content(current_url)
        processed_links += 1

        if not html_content:
            continue

        # Extrai novos links da página atual
        new_links = extract_links(html_content, current_url)
        print(f"Total de links encontrados em {current_url}: {len(new_links)}")
        for l in new_links:
            print("  ", l)


        links_to_visit.update(new_links - visited_links)

        # Extrai título e parágrafos da página atual
        title, paragraphs = extract_title_and_paragraphs(html_content)

        if not paragraphs:
            print(f"-- Nenhum parágrafo encontrado em: {current_url}")
            continue

        print(f"--> Processando {len(paragraphs)} parágrafos de: {current_url} (Título: {title})")
        inserted_count_page = 0
        for para_text in paragraphs:
            # Verifica duplicidade antes de inserir
            if not check_if_exists(conn, TABLE_NAME, para_text):
                insert_id = insert_data(conn, TABLE_NAME, title, para_text)
                if insert_id:
                    inserted_count_page += 1
                else:
                    # O erro já é impresso por insert_data
                    pass
            # else: # Log opcional para duplicados
            #     print(f"--- Parágrafo duplicado ignorado: {para_text[:30]}...")

        if inserted_count_page > 0:
            print(f"+++ {inserted_count_page} novos registros inseridos da página.")
            inserted_count_total += inserted_count_page

    print(f"\nScraping concluído.")
    print(f"Links processados: {processed_links}")
    print(f"Total de registros novos inseridos: {inserted_count_total}")

    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main() 