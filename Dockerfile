FROM python:3.10-slim

WORKDIR /app

# Instala dependências do sistema necessárias para rodar navegadores headless
RUN apt update && apt install -y \
    curl wget gnupg unzip \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 libxss1 libasound2 \
    libxshmfence1 libgbm1 libx11-xcb1 libxcb-dri3-0 libdrm2 \
    libglib2.0-0 libdbus-1-3 libatk1.0-0 libatspi2.0-0 \
    libx11-6 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxcb1 libxkbcommon0 libexpat1 libxrender1 \
    libfreetype6 libfontconfig1 libgdk-pixbuf2.0-0 libcairo2 \
    libcairo-gobject2 libpango-1.0-0 libpangocairo-1.0-0 \
    libwayland-client0 libwayland-server0 libwebp7 \
    libjpeg62-turbo libpng16-16 libopus0 libwebpdemux2 \
    libevent-2.1-7 libatomic1 libsecret-1-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências
COPY requirements.txt requirements.txt

# Instala dependências Python + Playwright + navegadores
RUN pip install --no-cache-dir -r requirements.txt && playwright install --with-deps

# Copia todo o projeto
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
