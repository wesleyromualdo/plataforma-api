from pyexpat import model
from sqlalchemy import select, delete, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz
AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioAnexoScript():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.AnexoScript).where(models.AnexoScript.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_tarefa_id(self, tarefa_id: int):
        try:
            stmt = select(models.AnexoScript).where(models.AnexoScript.tarefa_id == tarefa_id)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_setor_by_nome(self, tx_nome: str):
        try:
            stmt = select(models.AnexoScript).where(models.AnexoScript.tx_nome == tx_nome)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tarefa_id, tx_nome, nu_cpf, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.AnexoScript)
            
            if tx_nome:
                result = result.filter(models.AnexoScript.tx_nome == tx_nome)

            if nu_cpf:
                result = result.filter(models.AnexoScript.nu_cpf == nu_cpf)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.AnexoScriptPOST):
        try:
            anexo = await self.get_by_tarefa_id(orm.tarefa_id)
            
            db_orm = models.AnexoScript(
                tarefa_id = orm.tarefa_id,
                tx_nome = orm.tx_nome,
                tx_extensao = orm.tx_extensao,
                tx_tipo = orm.tx_tipo,
                nu_tamanho = orm.nu_tamanho,
                nu_arquivo = orm.nu_arquivo,
                nu_versao = (len(anexo) + 1),
                nu_cpf = orm.nu_cpf
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.tarefa_id).values(
                anexo_script_id = db_orm.id
            )
            self.db.execute(stmt)
            self.db.commit()

            return await self.get_by_id(db_orm.id)
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'detail': 'Erro ao anexar o script'}

    async def put(self, id, dt_download_ = ''):
        try:
            if dt_download_ is None or dt_download_ == '':
                utc_dt = datetime.now(timezone.utc)
                dt_download_ = utc_dt.astimezone(AMSP)
            else:
                dt_download_ = None

            stmt = update(models.AnexoScript).where(models.AnexoScript.id == id).values(
                dt_download = dt_download_
            )
            self.db.execute(stmt)
            self.db.commit()
            return await self.get_by_id(id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.AnexoScript).where(models.AnexoScript.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Registro excluido com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        