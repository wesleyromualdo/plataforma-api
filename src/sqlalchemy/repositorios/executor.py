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

class RepositorioExecutor():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.DownloadExecutor).where(models.DownloadExecutor.id == id).where(models.DownloadExecutor.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_automacao_ipmec(self, tx_ip_mac: int, automacao_id: int):
        try:
            stmt = select(models.DownloadExecutor).where(models.DownloadExecutor.tx_ip_mac == tx_ip_mac).where(models.DownloadExecutor.automacao_id == automacao_id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, automacao_id, setor_id, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.DownloadExecutor)
            
            if automacao_id:
                result = result.filter(models.DownloadExecutor.automacao_id == automacao_id)

            if setor_id:
                result = result.filter(models.DownloadExecutor.setor_id == setor_id)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            #filter(models.DownloadExecutor.bo_status == True)
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.DownloadExecutorPOST):
        try:
            utc_dt = datetime.now(timezone.utc)
            data = utc_dt.astimezone(AMSP)

            db_orm = models.DownloadExecutor(
                automacao_id = orm.automacao_id,
                setor_id = orm.setor_id,
                tx_nome = orm.tx_nome,
                nu_cpf = orm.nu_cpf,
                tx_json = orm.tx_json,
                tx_diretorio = orm.tx_diretorio,
                tx_hostname = orm.tx_hostname,
                tx_os = orm.tx_os,
                tx_ip = orm.tx_ip,
                tx_processador = orm.tx_processador,
                nu_cpu = orm.nu_cpu,
                tx_memoria = orm.tx_memoria,
                tx_hd = orm.tx_hd,
                tx_ip_mac = orm.tx_ip_mac,
                tx_hd_livre = orm.tx_hd_livre,
                bo_ativo = True,
                dt_alive = data
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'detail': f'Erro na execução: '+str(error)}

    async def atualiza_dados_executor(self, orm: schemas.DownloadExecutor):
        try:
            utc_dt = datetime.now(timezone.utc)
            data = utc_dt.astimezone(AMSP)

            stmt = update(models.DownloadExecutor).where(models.DownloadExecutor.id == orm.id).values(
                tx_hostname = orm.tx_hostname,
                tx_os = orm.tx_os,
                tx_ip = orm.tx_ip,
                tx_processador = orm.tx_processador,
                nu_cpu = orm.nu_cpu,
                tx_memoria = orm.tx_memoria,
                tx_hd = orm.tx_hd,
                tx_hd_livre = orm.tx_hd_livre,
                tx_diretorio = orm.tx_diretorio,
                tx_ip_mac = orm.tx_ip_mac,
                bo_status = True,
                bo_ativo = True,
                dt_alive = data
            )
            self.db.execute(stmt)
            self.db.commit()
            
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def atualiza_alive(self, orm: schemas.DownloadExecutor):
        try:
            utc_dt = datetime.now(timezone.utc)
            data = utc_dt.astimezone(AMSP)

            stmt = update(models.DownloadExecutor).where(models.DownloadExecutor.id == orm.id).values(
                bo_status = True,
                bo_ativo = True,
                dt_alive = data
            )
            self.db.execute(stmt)
            self.db.commit()            
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def stop_executor(self, id: int):
        try:
            stmt = update(models.DownloadExecutor).where(models.DownloadExecutor.id == id).values(
                bo_ativo = False,
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Executor parado com sucesso.'}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.DownloadExecutor).where(models.DownloadExecutor.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Executor inativado com sucesso.'}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        