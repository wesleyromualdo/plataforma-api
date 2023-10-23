
FROM python:3.8.5

WORKDIR /app

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt --no-cache-dir 
 
COPY . .

RUN python script.py

EXPOSE 8000
CMD python -m uvicorn server:app --host 0.0.0.0 --reload --reload-dir=src