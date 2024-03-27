from sqlalchemy import select, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, timezone
import pytz
AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioControleExecucao():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.ControleExecucao).where(models.ControleExecucao.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_nome(self, tx_descricao: str):
        try:
            stmt = select(models.ControleExecucao).where(models.ControleExecucao.tx_descricao == tx_descricao).where(models.ControleExecucao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_tarefa(self, tarefa_id: int):
        try:
            stmt = select(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id).where(models.ControleExecucao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tarefa_id, tx_descricao, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.ControleExecucao)
            
            if tx_descricao:
                result = result.filter(models.ControleExecucao.tx_descricao == tx_descricao)

            if tarefa_id:
                result = result.filter(models.ControleExecucao.tarefa_id == tarefa_id)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.ControleExecucao.bo_status == bo_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.ControleExecucaoPOST):
        try:
            db_orm = models.ControleExecucao(
                tx_descricao = orm.tx_descricao,
                tarefa_id = orm.tarefa_id,
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

    async def put(self, orm: schemas.ControleExecucao):
        try:
            stmt = update(models.ControleExecucao).where(models.ControleExecucao.id == orm.id).values(
                tx_descricao = orm.tx_descricao,
                tarefa_id = orm.tarefa_id,
                bo_status = orm.bo_status,
                tx_json = orm.tx_json
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            #self.db.refresh(db_orm)
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, tarefa_id: int):
        try:
            stmt = update(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'detail': 'Registro inativado com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        