from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas

from src.sqlalchemy.repositorios.kafka import RepositorioKafka
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from fastapi.routing import APIRoute
import os, json, pytz
from kafka import KafkaProducer

from datetime import datetime, timezone

AMSP = pytz.timezone('America/Sao_Paulo')

class RouteErrorHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as ex:
                if isinstance(ex, HTTPException):
                    raise ex
                print(ex)
                raise HTTPException(status_code=500, detail=str({'status': 1, 'detail': ex}))
        return custom_route_handler

router = APIRouter(route_class=RouteErrorHandler)

@router.post("/send", tags=['Kafka'], status_code=status.HTTP_200_OK)
async def send_message(msg: schemas.MessageKafka, usuario = Depends(obter_usuario_logado)):
    try:
        utc_dt = datetime.now(timezone.utc)
        data_atual = str(utc_dt.astimezone(AMSP))
        key = str(data_atual).replace(':', '').replace('-', '').replace(' ', '').replace('.', '')

        hash = str(data_atual).replace('-','').replace(' ','').replace('.','').replace(':','')

        producer = KafkaProducer(
            bootstrap_servers=msg.server,
            client_id=msg.client_id,
            compression_type=msg.compression_type,
            acks=msg.acks,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send(msg.topic, key=key ,value=msg.message)
        producer.flush()
        return {"detail": "Message sent to Kafka"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/consume", tags=['Kafka'], status_code=status.HTTP_200_OK)
async def consume_messages(topic: schemas.TopicKafka, background_tasks: BackgroundTasks, usuario = Depends(obter_usuario_logado)):
    background_tasks.add_task(RepositorioKafka.consume_kafka_messages, topic.server, topic.topic)
    return {"detail": f"Started consuming messages from topic {topic.topic}"}

@router.get("/topics", tags=['Kafka'], status_code=status.HTTP_200_OK)
async def get_topics_info(server: str, usuario = Depends(obter_usuario_logado)):
    try:
        topics = RepositorioKafka.list_topics(server)
        topics_info = {}
        for topic in topics:
            offsets = RepositorioKafka.get_topic_offsets(server, topic)
            topics_info[topic] = offsets
        return {"detail":topics_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", tags=['Kafka'], status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}