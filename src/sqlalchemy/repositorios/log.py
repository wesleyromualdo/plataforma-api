from pyexpat import model
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz, json
from elasticsearch import Elasticsearch

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioLogs():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Logs).where(models.Logs.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, historico_id, tx_descricao, pagina=0, tamanho_pagina=0):
        try:
            result = self.db.query(models.Logs).order_by(models.Logs.id.desc())
                
            if tx_descricao:
                result = result.filter(models.Logs.tx_descricao.in_(tx_descricao))
            
            if historico_id:
                result = result.filter(models.Logs.historico_tarefa_id == historico_id)

            if tamanho_pagina > 0:
                result = result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.Logs):
        try:
            db_orm = models.Logs(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                tx_descricao = orm.tx_descricao,
                tx_json = orm.tx_json
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Logs):
        try:
            stmt = update(models.Logs).where(models.Logs.id == orm.id).values(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                tx_descricao = orm.tx_descricao,
                tx_json = orm.tx_json
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            
            return self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = delete(models.Logs).where(models.Logs.id == id)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_logs_por_historico_id(self, historico_id: int):
        try:
            stmt = select(models.Logs).where(models.Logs.historico_tarefa_id == historico_id).order_by(models.Logs.id.desc())
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def inserir_doc_elastic(self, orm: schemas.LogsElastic):
        try:

            es = Elasticsearch(["http://elasticsearch.logging.svc.cluster.local:9200"])
            index_name = orm.index_name

            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name)
            
            res = es.index(index=index_name, body=orm.json_dados)
            return res['result']
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return traceback.format_exc()