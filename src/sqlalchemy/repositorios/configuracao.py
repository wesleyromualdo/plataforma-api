from pyexpat import model
from time import time
from sqlalchemy import select, delete, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz
AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioConfiguracao():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Configuracao).where(models.Configuracao.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_configuracao_by_chave(self, tx_chave: str):
        try:
            stmt = select(models.Configuracao).where(models.Configuracao.tx_chave == tx_chave).where(models.Configuracao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tx_chave, tarefa_id, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.Configuracao)
            if tx_chave:
                result = result.filter(models.Configuracao.tx_chave == tx_chave)

            if tarefa_id:
                result = result.filter(models.Configuracao.tarefa_id == tarefa_id)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.Configuracao.bo_status == bo_status)
            
            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            #print(str(result.statement.compile(self.db.bind)))
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.ConfiguracaoPOST):
        try:
            db_orm = models.Configuracao(
                tarefa_id = orm.tarefa_id,
                tx_chave = orm.tx_chave,
                tx_valor = orm.tx_valor
            )
            self.db.add(db_orm)
            self.db.commit()

            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.ConfiguracaoPOST):
        try:
            stmt = update(models.Configuracao).where(models.Configuracao.id == orm.id).values(
                tarefa_id = orm.tarefa_id,
                tx_chave = orm.tx_chave,
                tx_valor = orm.tx_valor
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.Configuracao).where(models.Configuracao.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'detail': 'Registro excluido com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        