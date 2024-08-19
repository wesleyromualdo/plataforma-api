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

    async def get_by_nome(self, tarefa_id:int, tx_descricao: str):
        try:
            stmt = (select(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id)
                    .where(models.ControleExecucao.tx_descricao == tx_descricao)
                    .where(models.ControleExecucao.bo_status == True)
                    .order_by(models.ControleExecucao.dt_cadastro.desc()))
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_chave(self, tarefa_id:int, tx_chave: str):
        try:
            stmt = (select(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id)
                        .where(models.ControleExecucao.tx_chave == tx_chave)
                        .where(models.ControleExecucao.bo_status == True)
                        .order_by(models.ControleExecucao.dt_cadastro.desc()))
            db_orm = self.db.execute(stmt).scalars().all()
            
            return db_orm
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error

    async def get_by_situacao(self, tarefa_id:int, tx_situacao: str):
        try:
            stmt = (select(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id)
                    .where(models.ControleExecucao.tx_situacao == tx_situacao)
                    .where(models.ControleExecucao.bo_status == True)
                    .order_by(models.ControleExecucao.dt_cadastro.desc()))
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_tarefa(self, tarefa_id: int):
        try:
            stmt = select(models.ControleExecucao).where(models.ControleExecucao.tarefa_id == tarefa_id).where(models.ControleExecucao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, tarefa_id, tx_chave, tx_descricao, bo_status, pagina, tamanho_pagina):
        try:
            result = self.db.query(models.ControleExecucao)
            
            if tx_chave:
                result = result.filter(models.ControleExecucao.tx_chave == tx_chave)

            if tx_descricao:
                result = result.filter(models.ControleExecucao.tx_descricao == tx_descricao)

            if tarefa_id:
                result = result.filter(models.ControleExecucao.tarefa_id == tarefa_id)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.ControleExecucao.bo_status == bo_status)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error
        
    async def get_all_by_dash(self, tarefa_id, cliente_id, tx_chave, dt_inicio, dt_fim, tx_descricao, tx_situacao, pagina, tamanho_pagina):
        try:
            
            filtros = []
            if tx_chave:
                filtros.append(f" AND c.tx_chave = '{tx_chave}'")

            if tx_descricao:
                filtros.append(f" AND c.tx_descricao = '{tx_descricao}'")

            if tarefa_id:
                filtros.append(f" AND c.tarefa_id = {tarefa_id}")

            if tx_situacao:
                filtros.append(f" AND c.tx_situacao = '{tx_situacao}'")

            if dt_inicio and dt_fim:
                filtros.append(f" AND c.dt_cadastro BETWEEN to_timestamp('{dt_inicio} 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp('{dt_fim} 23:59:59', 'YYYY-MM-DD HH24:MI:SS')")
            else:
                if dt_inicio:
                    filtros.append(f" AND c.dt_cadastro = to_timestamp('{dt_inicio} 00:00:00', 'YYYY-MM-DD HH24:MI:SS')")

                if dt_fim:
                    filtros.append(f" AND c.dt_cadastro = to_timestamp('{dt_fim} 00:00:00', 'YYYY-MM-DD HH24:MI:SS')")

                #WHERE th.dt_inicio BETWEEN to_timestamp('{dt_inicio} 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp('{dt_fim} 23:59:59', 'YYYY-MM-DD HH24:MI:SS')

            '''sql_count = f"""SELECT COUNT(*) 
                        FROM controle_execucao c
                        INNER JOIN tarefa t ON t.id = c.tarefa_id  
                        WHERE c.bo_status = TRUE
                        {''.join(filtros)};"""
            total =self.db.execute(sql_count).scalars().first()'''

            paginacao = ''
            if tamanho_pagina > 0:
                offset = (pagina - 1) * tamanho_pagina
                paginacao = f"LIMIT {tamanho_pagina} OFFSET {offset}"

            sql = f"""WITH max_dt_cadastro AS (
                        SELECT tx_chave, MAX(dt_cadastro) AS max_dt
                        FROM public.controle_execucao
                        GROUP BY tx_chave
                    )
                    SELECT c.id, c.tarefa_id, t.tx_nome, c.tx_descricao, c.dt_cadastro, to_char(c.dt_cadastro, 'DD/MM/YYYY HH24:MI:SS') AS dt_cadastro_formata, 
                        c.bo_status, c.tx_json, c.bo_status_code, c.tx_chave, c.tx_situacao, c.tx_resumo, 
                        TO_CHAR(c.tx_tempo::INTERVAL, 'HH24:MI:SS') AS tempo_formatado, c.dt_inicio, c.dt_fim, c.tx_imgbase64 
                    FROM controle_execucao c
                        INNER JOIN tarefa t ON t.id = c.tarefa_id  
                        INNER JOIN max_dt_cadastro mdc ON c.tx_chave = mdc.tx_chave AND c.dt_cadastro = mdc.max_dt
                    WHERE c.bo_status = TRUE
                        AND t.cliente_id = {cliente_id}
                    {''.join(filtros)}
                    /*AND c.dt_cadastro  = (
                        SELECT max(dt_cadastro) FROM public.controle_execucao WHERE tx_chave = c.tx_chave
                    )*/
                    ORDER BY c.dt_cadastro DESC
                    {paginacao};"""
            
            return {'data':self.db.execute(sql).all(), 'total':0}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error

    async def post(self, orm: schemas.ControleExecucaoPOST):
        try:
            #diretorio_image = utils.salvar_imagem_base64_diretorio(orm.tx_imgbase64)
            db_orm = models.ControleExecucao(
                tx_descricao = orm.tx_descricao,
                tarefa_id = orm.tarefa_id,
                tx_json = orm.tx_json,
                bo_status_code = orm.bo_status_code,
                tx_chave = orm.tx_chave,
                tx_situacao = orm.tx_situacao,
                tx_resumo = orm.tx_resumo,
                dt_inicio = orm.dt_inicio,
                dt_fim = orm.dt_fim,
                tx_tempo = orm.tx_tempo,
                tx_imgbase64 = orm.tx_imgbase64
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error

    async def put(self, orm: schemas.ControleExecucao):
        try:
            #diretorio_image = utils.salvar_imagem_base64_diretorio(orm.tx_imgbase64)

            stmt = update(models.ControleExecucao).where(models.ControleExecucao.id == orm.id).values(
                tx_descricao = orm.tx_descricao,
                tarefa_id = orm.tarefa_id,
                tx_json = orm.tx_json,
                bo_status_code = orm.bo_status_code,
                tx_chave = orm.tx_chave,
                tx_situacao = orm.tx_situacao,
                tx_resumo = orm.tx_resumo,
                dt_inicio = orm.dt_inicio,
                dt_fim = orm.dt_fim,
                tx_tempo = orm.tx_tempo,
                tx_imgbase64 = orm.tx_imgbase64
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            #self.db.refresh(db_orm)
            return await self.get_by_id(orm.id)
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error

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
        