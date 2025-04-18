import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'db')
DB_PATH = os.path.join(DB_DIR, 'lumia.db')

# Garante que o diretório db exista
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

def create_connection():
    """ Cria uma conexão com o banco de dados SQLite especificado por DB_PATH """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"Conexão com SQLite DB versão {sqlite3.sqlite_version} bem-sucedida.")
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados SQLite: {e}")
    return conn

def create_table(conn, create_table_sql):
    """ Cria uma tabela a partir da instrução create_table_sql
    :param conn: Objeto de conexão
    :param create_table_sql: Uma instrução CREATE TABLE
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela: {e}")

def insert_data(conn, table, pergunta, resposta):
    """ Insere um novo registro na tabela especificada """
    sql = f''' INSERT INTO {table}(pergunta,resposta)
              VALUES(?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (pergunta, resposta))
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        print(f"Erro ao inserir dados na tabela {table}: {e}")
        return None

# Exemplo de uso (pode ser removido ou comentado)
if __name__ == '__main__':
    sql_create_prape_table = """ CREATE TABLE IF NOT EXISTS prape (
                                        id integer PRIMARY KEY,
                                        pergunta text,
                                        resposta text NOT NULL
                                    ); """

    conn = create_connection()

    if conn is not None:
        create_table(conn, sql_create_prape_table)
        # Exemplo de inserção
        # insert_id = insert_data(conn, 'prape', 'Qual o horário de funcionamento?', 'De segunda a sexta, das 8h às 17h.')
        # if insert_id:
        #     print(f"Registro inserido com ID: {insert_id}")
        conn.close()
    else:
        print("Erro! Não foi possível criar a conexão com o banco de dados.") 