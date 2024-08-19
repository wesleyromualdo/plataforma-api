FROM python:3.8.5 AS build-app-image

WORKDIR /app

# Instalar Git
RUN apt-get update && apt-get install -y git

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir 
 
COPY . .

ENV API_ENVIRONMENT=development

#RUN python script.py

EXPOSE 3000
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000", "--reload", "--reload-dir=src"]