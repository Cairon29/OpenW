FROM python:3.10-slim

# Instalar dependencias del sistema (de construcción y ejecución)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    netcat-openbsd \
    dos2unix \
    build-essential \
    python3-dev \
    libpq-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Configurar variables de entorno y permisos
ENV PYTHONPATH="${PYTHONPATH}:/app"
ENV FLASK_APP=app:create_app
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Exponer el puerto y ejecutar
EXPOSE 2222
ENTRYPOINT ["sh","/app/entrypoint.sh"]