from sqlalchemy.orm import Session
from src.utils import utils
import traceback
from datetime import datetime, timezone
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
import pytz, threading, json

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioKafka():

    def __init__(self, db: Session):
        self.db = db

    def list_topics(self, server: str):
        admin_client = KafkaAdminClient(bootstrap_servers=server)
        topics = admin_client.list_topics()
        return topics
    
    def consume_kafka_messages(self, server: str, topic: str):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=server,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id='my-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                fetch_min_bytes=1,
                fetch_max_wait_ms=500,
                max_poll_records=100
            )
            for message in consumer:
                return {"detail":f"Consumed message from {topic}: {message.value}"}
        except Exception as e:
            return {"detail":f"Failed to consume messages: {e}"}

    # Iniciar o consumidor Kafka em uma thread separada
    def start_consumer(self, server: str, topic: str):
        threading.Thread(target=self.consume_kafka_messages, args=(server, topic), daemon=True).start()

    def get_topic_offsets(self, server: str, topic: str):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=server,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id=None
            )
            partitions = consumer.partitions_for_topic(topic)
            if partitions is None:
                return None

            earliest_offsets = consumer.beginning_offsets(partitions)
            latest_offsets = consumer.end_offsets(partitions)

            processed_messages = 0
            unprocessed_messages = 0

            for partition in partitions:
                earliest = earliest_offsets[partition]
                latest = latest_offsets[partition]
                processed_messages += latest - earliest
                unprocessed_messages += latest - earliest

            return {
                "processed_messages": processed_messages,
                "unprocessed_messages": unprocessed_messages
            }
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        