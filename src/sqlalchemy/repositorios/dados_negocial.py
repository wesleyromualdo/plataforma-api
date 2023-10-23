from pyexpat import model
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioDadosNegocial():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.DadoNegocial).where(models.DadoNegocial.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, historico_id, tx_descricao, tx_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.DadoNegocial)
            if tx_descricao:
                result = result.filter(models.DadoNegocial.tx_descricao.in_(tx_descricao))
            
            if historico_id:
                result = result.filter(models.DadoNegocial.historico_tarefa_id == historico_id)
            
            if str(tx_status):
                result = result.filter(models.DadoNegocial.tx_status == tx_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.DadoNegocial):
        try:
            db_orm = models.DadoNegocial(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                dt_inicio = orm.dt_inicio,
                dt_fim = orm.dt_fim,
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

    async def put(self, orm: schemas.DadoNegocial):
        try:
            stmt = update(models.DadoNegocial).where(models.DadoNegocial.id == orm.id).values(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                dt_inicio = orm.dt_inicio,
                dt_fim = orm.dt_fim,
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
            stmt = delete(models.DadoNegocial).where(models.DadoNegocial.id == id)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        