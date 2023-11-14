
FROM python:3.8.5 as build-app-image

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir 
 
COPY . .

ENV API_ENVIRONMENT development

RUN python script.py

EXPOSE 8000
CMD python -m uvicorn server:app --host 0.0.0.0 --reload --reload-dir=src