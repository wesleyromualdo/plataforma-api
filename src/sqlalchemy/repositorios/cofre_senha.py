from sqlalchemy import select, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, timezone
import pytz
AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioCofreSenha():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.CofreSenha).where(models.CofreSenha.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_nome(self, tx_nome: str, setor_id: int):
        try:
            stmt = select(models.CofreSenha).where(models.CofreSenha.tx_nome == tx_nome).where(models.CofreSenha.bo_status == True).where(models.CofreSenha.setor_id == setor_id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_setor(self, setor_id: int):
        try:
            stmt = select(models.CofreSenha).where(models.CofreSenha.setor_id == setor_id).where(models.CofreSenha.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, setor_id, tx_nome, tx_usuario, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.CofreSenha)
            
            if tx_nome:
                result = result.filter(models.CofreSenha.tx_nome == tx_nome)

            if tx_usuario:
                result = result.filter(models.CofreSenha.tx_usuario == tx_usuario)

            if setor_id:
                result = result.filter(models.CofreSenha.setor_id == setor_id)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.CofreSenha.bo_status == bo_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.CofreSenhaPOST):
        try:
            db_orm = models.CofreSenha(
                tx_nome = orm.tx_nome,
                tx_usuario = orm.tx_usuario,
                tx_senha = orm.tx_senha,
                setor_id = orm.setor_id
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.CofreSenha):
        try:
            stmt = update(models.CofreSenha).where(models.CofreSenha.id == orm.id).values(
                tx_nome = orm.tx_nome,
                tx_usuario = orm.tx_usuario,
                tx_senha = orm.tx_senha,
                setor_id = orm.setor_id
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            #self.db.refresh(db_orm)
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.CofreSenha).where(models.CofreSenha.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Registro inativado com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        