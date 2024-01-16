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

class RepositorioCliente():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Cliente).where(models.Cliente.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_cliente_by_nome(self, tx_nome: str):
        try:
            stmt = select(models.Cliente).where(models.Cliente.tx_nome == tx_nome)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_cliente_by_usuario(self, nu_cpf: str):
        try:
            j = join(models.Cliente, models.UsuarioCliente, models.Cliente.id == models.UsuarioCliente.cliente_id)
            stmt = select(models.Cliente).select_from(j).where(models.UsuarioCliente.nu_cpf == nu_cpf).order_by(models.UsuarioCliente.dt_ultimoacesso.desc())
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tx_sigla, tx_nome, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.Cliente)
            
            if tx_nome:
                result = result.filter(models.Cliente.tx_nome == tx_nome)

            if tx_sigla:
                result = result.filter(models.Cliente.tx_sigla == tx_sigla)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.Cliente.bo_status == bo_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.ClientePOST):
        try:
            db_orm = models.Cliente(
                tx_nome = orm.tx_nome,
                tx_sigla = orm.tx_sigla,
                bo_status = orm.bo_status,
                nu_worker = orm.nu_worker
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Cliente):
        try:
            stmt = update(models.Cliente).where(models.Cliente.id == orm.id).values(
                tx_nome = orm.tx_nome,
                tx_sigla = orm.tx_sigla,
                bo_status = orm.bo_status,
                nu_worker = orm.nu_worker
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()

            #self.db.refresh(db_orm)
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def altera_ultimo_acesso_usuario(self, orm: schemas.UsuarioClienteAcesso):
        try:
            utc_dt = datetime.now(timezone.utc)
            data = utc_dt.astimezone(AMSP)
            stmt = update(models.UsuarioCliente).where(models.UsuarioCliente.nu_cpf == orm.nu_cpf).where(models.UsuarioCliente.cliente_id == orm.cliente_id).values(
                dt_ultimoacesso = data
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            return True
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.Cliente).where(models.Cliente.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Registro excluido com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        