import asyncio
import sys
import os
import sqlite3
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page

# Adiciona o diretório pai ao sys.path para encontrar o módulo utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.db_handler import create_connection, create_table, insert_data

BASE_URL = "https://www.ufpb.br/"
TABLE_NAME = "prape"
IGNORE_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".css", ".js", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".rar", ".mp3", ".mp4", ".avi", ".mov", ".svg", ".xml", ".ico"]
MIN_WORDS_PARAGRAPH = 10

visited_links = set()

def is_relevant_link(url, base_url):
    """ Verifica se um link pertence ao domínio ufpb.br e não é um arquivo ignorado. """
    try:
        parsed_url = urlparse(url)

        # Ignora links sem scheme http/https
        if not parsed_url.scheme in ['http', 'https']:
            return False

        # Permite apenas links dentro de *.ufpb.br
        if not parsed_url.netloc.endswith(".ufpb.br"):
             return False

        # Ignora se o path termina com uma extensão proibida
        path = parsed_url.path.lower()
        if any(path.endswith(ext) for ext in IGNORE_EXTENSIONS):
            return False

        return True
    except Exception as e:
        print(f"Erro ao analisar link {url}: {e}")
        return False

def check_if_exists(conn, table, resposta):
    """ Verifica se um registro com a mesma resposta já existe na tabela. """
    sql = f''' SELECT 1 FROM {table} WHERE resposta = ? LIMIT 1 '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (resposta,))
        exists = cur.fetchone() is not None
        return exists
    except sqlite3.Error as e:
        print(f"Erro ao verificar existência na tabela {table}: {e}")
        return False

async def process_page(page: Page, current_url: str, conn) -> set:
    """ Extrai links e conteúdo de uma página, insere no DB e retorna novos links. """
    new_links_found = set()
    inserted_count_page = 0
    paragraphs_found_count = 0
    page_title = "Título não encontrado"

    try:
        # --- Extração de Links ---
        link_locators = page.locator('a[href]')
        count = await link_locators.count()
        for i in range(count):
            href = await link_locators.nth(i).get_attribute('href')
            if href:
                try:
                    absolute_url = urljoin(current_url, href.strip())
                    parsed_abs = urlparse(absolute_url)
                    normalized_url = parsed_abs._replace(fragment='').geturl().strip()
                    if is_relevant_link(normalized_url, BASE_URL):
                        new_links_found.add(normalized_url)
                except Exception as e_link_proc:
                    print(f"Erro processando href '{href}': {e_link_proc}")

        # --- Extração de Conteúdo ---
        page_title = await page.title() or "Título não encontrado"

        paragraphs = []
        para_locators = page.locator('p')
        para_count = await para_locators.count()
        paragraphs_found_count = para_count # Conta todos os <p> encontrados
        for i in range(para_count):
            p_text = await para_locators.nth(i).text_content()
            if p_text:
                cleaned_text = ' '.join(p_text.split())
                if cleaned_text and len(cleaned_text.split()) >= MIN_WORDS_PARAGRAPH:
                    paragraphs.append(cleaned_text)

        # --- Inserção no Banco de Dados ---
        if paragraphs:
            for para_text in paragraphs:
                if not check_if_exists(conn, TABLE_NAME, para_text):
                    # ATENÇÃO: Inserindo dados de TODO o site na tabela 'prape'!
                    insert_id = insert_data(conn, TABLE_NAME, page_title, para_text)
                    if insert_id:
                        inserted_count_page += 1

    except Exception as e:
        print(f"Erro inesperado ao processar conteúdo/links de {current_url}: {e}")

    finally:
        # --- Log da Página Processada ---
        print(f"  Título: {page_title}")
        print(f"  Parágrafos encontrados: {paragraphs_found_count} | Válidos (>{MIN_WORDS_PARAGRAPH-1} palavras): {len(paragraphs)} | Inseridos: {inserted_count_page}")

    return new_links_found

async def scrape_prape():
    """ Realiza o scraping recursivo completo do domínio ufpb.br usando Playwright. """
    print(f"Iniciando scraping recursivo completo de: {BASE_URL}")
    global visited_links
    links_to_visit = {BASE_URL}
    processed_links_count = 0

    conn = create_connection()
    if conn is None:
        print("Erro: Não foi possível conectar ao banco de dados.")
        return

    # Garante que a tabela existe
    sql_create_prape_table = f""" CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                                        id integer PRIMARY KEY,
                                        pergunta text, -- Título da página
                                        resposta text NOT NULL,
                                        UNIQUE(resposta)
                                    ); """
    create_table(conn, sql_create_prape_table)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
            print("Usando Chromium.")
        except Exception as e_chromium:
            print(f"Falha ao iniciar Chromium: {e_chromium}. Tentando Firefox...")
            try:
                browser = await p.firefox.launch()
                print("Usando Firefox.")
            except Exception as e_firefox:
                print(f"Falha ao iniciar Firefox: {e_firefox}. Tentando WebKit...")
                try:
                    browser = await p.webkit.launch()
                    print("Usando WebKit.")
                except Exception as e_webkit:
                    print(f"Falha ao iniciar todos os navegadores: {e_webkit}")
                    if conn:
                        conn.close()
                    return

        page_context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await page_context.new_page()

        while links_to_visit:
            current_url = links_to_visit.pop()
            if current_url in visited_links:
                continue

            visited_links.add(current_url)
            processed_links_count += 1
            print(f"\n[{processed_links_count}] Visitando: {current_url}")

            try:
                await page.goto(current_url, timeout=60000, wait_until='domcontentloaded')

                # Processa a página atual (extrai links e conteúdo)
                new_links = await process_page(page, current_url, conn)
                links_to_visit.update(new_links - visited_links)

            except PlaywrightTimeoutError:
                print(f"Erro de Timeout ao acessar: {current_url}")
            except Exception as e:
                print(f"Erro inesperado ao visitar/processar {current_url}: {type(e).__name__} - {e}")
            # Não fecha a página aqui para reutilizar

        await page.close()
        await page_context.close()
        await browser.close()

    print(f"\n--- Scraping Recursivo Concluído ---")
    print(f"Total de links únicos visitados: {len(visited_links)}")

    if conn:
        conn.close()
        print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    # Para rodar Playwright pela primeira vez, pode ser necessário instalar os navegadores:
    # Execute no terminal: playwright install
    # (ou playwright install chromium)
    asyncio.run(scrape_prape()) 