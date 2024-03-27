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

class RepositorioPerfil():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Perfil).where(models.Perfil.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_perfil_by_nome(self, tx_nome: str):
        try:
            stmt = select(models.Perfil).where(models.Perfil.tx_nome == tx_nome).where(models.Perfil.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_perfil_by_usuario(self, nu_cpf: str):
        try:
            j = join(models.Perfil, models.PerfilUsuario, models.Perfil.id == models.PerfilUsuario.perfil_id)
            stmt = select(models.Perfil).select_from(j).where(models.PerfilUsuario.nu_cpf == nu_cpf).where(models.Perfil.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tx_nome, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.Perfil)
            if tx_nome:
                result = result.filter(models.Perfil.tx_nome == tx_nome)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.Perfil.bo_status == bo_status)
            
            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            result = result.filter(models.Perfil.constante_virtual != 'ROBO_WORKERS')
            #print(str(result.statement.compile(self.db.bind)))
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.PerfilPOST):
        try:
            db_orm = models.Perfil(
                tx_nome = orm.tx_nome,
                bo_status = orm.bo_status,
                tx_finalidade = orm.tx_finalidade,
                bo_superuser = orm.bo_superuser,
                bo_delegar = orm.bo_delegar,
                constante_virtual = orm.constante_virtual
            )
            self.db.add(db_orm)
            self.db.commit()
            
            for menu in orm.menu:
                db_menu = models.PerfilMenu(
                    menu_id = menu.id,
                    perfil_id = db_orm.id,
                    cliente_id = menu.cliente_id
                )            
            self.db.add(db_menu)
            self.db.commit()

            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.PerfilPOST):
        try:
            stmt = update(models.Perfil).where(models.Perfil.id == orm.id).values(
                tx_nome = orm.tx_nome,
                bo_status = orm.bo_status,
                tx_finalidade = orm.tx_finalidade,
                bo_superuser = orm.bo_superuser,
                bo_delegar = orm.bo_delegar,
                constante_virtual = orm.constante_virtual
            )
            db_orm = self.db.execute(stmt)

            await self.deleteMenu(orm.id)
            for menu in orm.menu:
                db_menu = models.PerfilMenu(
                    menu_id = menu.id,
                    perfil_id = orm.id,
                    cliente_id = menu.cliente_id
                )
                self.db.add(db_menu)

            self.db.commit()
            
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.Perfil).where(models.Perfil.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'detail': 'Registro excluido com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def deleteMenu(self, id_perfil: int):
        try:
            stmt = delete(models.PerfilMenu).where(models.PerfilMenu.perfil_id == id_perfil)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        