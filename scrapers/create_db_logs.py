import sqlite3

conn = sqlite3.connect("db/lumia.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    agente TEXT,
    data_hora TEXT DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()
conn.close()

print("Tabela de logs criada com sucesso.")
