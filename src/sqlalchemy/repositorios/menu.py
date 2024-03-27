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

class RepositorioMenu():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Menu).where(models.Menu.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_menu_by_perfil(self, perfil_id: int):
        try:
            j = join(models.Menu, models.PerfilMenu, models.Menu.id == models.PerfilMenu.menu_id)
            stmt = select(models.Menu).select_from(j).where(models.PerfilMenu.perfil_id == perfil_id).where(models.Menu.bo_status==True).order_by(models.Menu.nu_ordem.asc())
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_menu_by_nome(self, tx_nome: str):
        try:
            stmt = select(models.Menu).where(models.Menu.tx_nome == tx_nome)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, nu_codigo, tx_nome, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.Menu).order_by(models.Menu.nu_ordem.asc())
            if tx_nome:
                result = result.filter(models.Menu.tx_nome == tx_nome)
            
            if nu_codigo:
                result = result.filter(models.Menu.nu_codigo == nu_codigo)
            
            if str(bo_status):
                result = result.filter(models.Menu.bo_status == bo_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.Menu):
        try:
            db_orm = models.Menu(
                nu_codigo = orm.nu_codigo,
                tx_nome = orm.tx_nome,
                tx_link = orm.tx_link,
                tx_icon = orm.tx_icon,
                nu_ordem = orm.nu_ordem,
                bo_status = orm.bo_status
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Menu):
        try:
            stmt = update(models.Menu).where(models.Menu.id == orm.id).values(
            nu_codigo = orm.nu_codigo,
                tx_nome = orm.tx_nome,
                tx_link = orm.tx_link,
                tx_icon = orm.tx_icon,
                nu_ordem = orm.nu_ordem,
                bo_status = orm.bo_status
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
            stmt = update(models.Menu).where(models.Menu.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'detail': 'Registro excluido com sucesso.'}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        