from fastapi import FastAPI
import uvicorn
import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir que os módulos sejam encontrados
sys.path.append(os.path.dirname(__file__))

# Importa o router do módulo de rotas
from routes import assistente

app = FastAPI(
    title="LumIA - Assistente Virtual Acadêmico",
    description="API para interagir com o assistente virtual LumIA.",
    version="0.1.0"
)

# Inclui as rotas definidas em routes/assistente.py
app.include_router(assistente.router, prefix="/api", tags=["Assistente"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API do LumIA! Acesse /docs para a documentação interativa."}

# Bloco para rodar o servidor com Uvicorn quando o script é executado diretamente
if __name__ == "__main__":
    # Verifica se está rodando dentro do Docker para definir o host corretamente
    # HOST = "0.0.0.0" if os.getenv("RUNNING_IN_DOCKER") else "127.0.0.1"
    # Simplificando para sempre usar 0.0.0.0 que funciona tanto local quanto Docker
    HOST = "0.0.0.0"
    PORT = 8000
    print(f"Iniciando servidor Uvicorn em {HOST}:{PORT}")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True) # reload=True útil para desenvolvimento 