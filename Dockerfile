FROM python:3.10-slim-buster AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libbz2-dev \
    gcc \
    libc-dev \
    libffi-dev \
    libssl-dev \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir 
 
COPY . .

ENV API_ENVIRONMENT=development

EXPOSE 3000
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000", "--reload", "--reload-dir=src"]