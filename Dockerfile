FROM python:3.11-slim

# Define um diretório de trabalho temporário
WORKDIR /

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gnupg2 \
  && apt-get update \
  && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos do host para o container
COPY . .

# Diretório de trabalho para /src
WORKDIR /src

# Comando de inicialização
CMD ["python", "app.py"]