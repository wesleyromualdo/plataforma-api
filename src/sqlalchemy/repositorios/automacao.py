from pyexpat import model
from sqlalchemy import select, delete, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, timezone
from src.sqlalchemy.repositorios import usuario

import json
from src.providers import hash_provider
import string, boto3
from dotenv import dotenv_values

import pytz

import random
import shutil, os
from zipfile import ZipFile

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioAutomacao():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Automacao).where(models.Automacao.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_txjson_by_id(self, id: int):
        try:
            stmt = f"""SELECT id, tx_nome, tx_json FROM automacao a WHERE id = {id} AND bo_status = true;"""
            db_orm = self.db.execute(stmt).first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_txjson_by_constante_virtual(self, constante_virtual: str):
        try:
            stmt = f"""SELECT id, tx_nome, tx_json FROM automacao a WHERE tx_constante_virtual = '{constante_virtual}' AND bo_status = true;"""
            db_orm = self.db.execute(stmt).first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_id_sql(self, id: int):
        try:
            stmt = f"""WITH downloadworker AS (
                            SELECT count(id) AS tot_donwload, automacao_id FROM public.download_worker GROUP BY automacao_id
                        )
                        SELECT *, COALESCE(tot_donwload, 0) AS total_donwload 
                        FROM public.automacao a 
                            LEFT JOIN downloadworker d ON d.automacao_id = a.id
                        WHERE a.id = {id} AND a.bo_status = true;"""
            db_orm = self.db.execute(stmt).first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_automacao_by_nome(self, tx_nome: str):
        try:
            stmt = select(models.Automacao).where(models.Automacao.tx_nome == tx_nome).where(models.Automacao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_automacao_by_usuario(self, nu_cpf: str, cliente_id: str):
        try:
            '''SELECT count(th.id) AS qtd_tarefas, th.automacao_id FROM tarefa_historico th
						INNER JOIN tarefa t ON t.id = th.tarefa_id
                        WHERE t.cliente_id = {cliente_id} AND t.bo_status = TRUE
                        	AND th.automacao_id IS NOT NULL
                        GROUP BY th.automacao_id'''

            stmt = f"""WITH tarefa_tmp AS (
                        SELECT count(th.id) AS qtd_tarefas, th.automacao_id FROM tarefa th
                        WHERE th.cliente_id = {cliente_id} AND th.bo_status = TRUE
                        	AND th.automacao_id IS NOT NULL
                        GROUP BY th.automacao_id
                    )
                    SELECT COALESCE(qtd_tarefas,0) AS qtd_tarefas, a.id, a.tx_nome, a.tx_descricao, COALESCE(a.nu_qtd_tarefa,0) AS nu_qtd_tarefa 
                    FROM automacao a 
                        INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                        LEFT JOIN tarefa_tmp tp ON tp.automacao_id = a.id
                    WHERE au.nu_cpf = '{nu_cpf}'
                        AND a.cliente_id = {cliente_id}
                        AND a.bo_status = TRUE"""

            '''j = join(models.Automacao, models.AutomacaoUsuario, models.Automacao.id == models.AutomacaoUsuario.automacao_id)
            stmt = select(models.Automacao).select_from(j).where(models.AutomacaoUsuario.nu_cpf == nu_cpf).where(models.Automacao.cliente_id == cliente_id)'''
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_usuario_by_worker(self, nu_cpf: str, tx_ip_mac: str):
        try:
            j = join(models.Automacao, models.AutomacaoUsuario, models.Automacao.id == models.AutomacaoUsuario.automacao_id)
            stmt = select(models.Automacao).select_from(j).where(models.AutomacaoUsuario.nu_cpf == nu_cpf).where(models.Automacao.tx_ip_mac == tx_ip_mac)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_automacao_by_usuario_dashboard(self, nu_cpf: str, cliente_id: str, periodo=10):
        try:
            stmt = f"""SELECT DISTINCT a.id, a.cliente_id, a.tx_nome, a.tx_descricao, a.bo_status, a.tx_json, a.dt_inclusao 
                    FROM automacao a
                        INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                        INNER JOIN tarefa t ON t.automacao_id = a.id AND t.bo_status = TRUE AND t.cliente_id = {cliente_id}
                        INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.dt_inicio BETWEEN (now() - INTERVAL '{periodo} day') AND now()
                    WHERE a.bo_status = TRUE
                        AND au.nu_cpf = '{nu_cpf}'"""
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_cliente(self, cliente_id: int):
        try:
            stmt = select(models.Automacao).where(models.Automacao.cliente_id == cliente_id).where(models.Automacao.bo_status == True)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, cliente_id, tx_nome, bo_status, nu_cpf, pagina=0, tamanho_pagina=0):
        try:
            #j = join(models.Tarefa, models.Automacao, models.Automacao.id == models.Tarefa.automacao_id)

            '''result = self.db.query(models.Automacao)
            if cliente_id:
                result = result.filter(models.Automacao.cliente_id == cliente_id)

            if tx_nome:
                result = result.filter(models.Automacao.tx_nome == tx_nome)

            #result = result.filter(models.Automacao.bo_status == False)
            if str(bo_status):
                result = result.filter(models.Automacao.bo_status == bo_status)'''

            filtro = ''
            if cliente_id:
                filtro += f" and a.cliente_id = {cliente_id}"

            #if nu_cpf:
            #    filtro += f" and au.nu_cpf = '{nu_cpf}'"

            if tx_nome:
                filtro += f" and a.tx_nome ilike '%{tx_nome}%'"

            sql = f"""WITH tarefa_execucao AS (
                        SELECT count(id) AS qtd_execucao, automacao_id, sum(tempo) AS tempo_execucao, max(dt_inicio) AS dt_inicio, max(dt_fim) AS dt_fim
                        FROM(    
                            SELECT th.id, t.automacao_id, CASE WHEN th.dt_inicio > th.dt_fim THEN 0 ELSE COALESCE(DATEDIFF('second', th.dt_inicio::timestamp, th.dt_fim::timestamp),0) END AS segundos,
                                CASE WHEN th.dt_inicio < th.dt_fim THEN (th.dt_fim::timestamp - th.dt_inicio::timestamp) END AS tempo, th.dt_inicio,
                                (SELECT dt_fim FROM tarefa_historico WHERE automacao_id = th.automacao_id ORDER BY id DESC LIMIT 1) AS dt_fim
                            FROM tarefa t 
                                INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND t.automacao_id =th.automacao_id
                            WHERE t.bo_status = TRUE        
                        ) AS foo
                        GROUP BY automacao_id    
                    ),
                    qtd_tarefas AS (
                        SELECT count(id) AS tarefas, automacao_id FROM tarefa t WHERE bo_status = TRUE
                        GROUP BY automacao_id
                    )
                    SELECT DISTINCT a.id, a.cliente_id, a.tx_nome, a.tx_descricao, a.bo_status, 
                        a.dt_inclusao, a.nu_qtd_tarefa, a.nu_cpf, a.nu_qtd_download ,
                        COALESCE(t.qtd_execucao,0) AS qtd_execucao, coalesce(qt.tarefas,0) AS tarefas_vinculadas,
                        t.tempo_execucao::varchar, t.dt_inicio, t.dt_fim
                    FROM automacao a
                        LEFT JOIN automacao_usuario au ON au.automacao_id = a.id
                        LEFT JOIN tarefa_execucao t ON t.automacao_id = a.id
                        LEFT JOIN qtd_tarefas qt ON qt.automacao_id = a.id
                    WHERE a.bo_status = {bo_status} {filtro}"""
            
            #if tamanho_pagina > 0:
            #    result.offset(pagina).limit(tamanho_pagina)
            
            result = self.db.execute(sql)
            return result.all()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def gerar_worker_cliente(self, dados):
        try:
            cpf = ''
            for i in range(0,10):
                cpf = str(cpf)+str(random.randint(0,9))

            dir_workers = os.getcwd()+'/worker_tpl'
            dir_workers = dir_workers.replace('/', '/')
            workers = 'worker-setup.zip'

            sql = f"SELECT tx_sigla FROM cliente s WHERE id = {dados.cliente_id}"
            cliente = self.db.execute(sql).first()
            tx_sigla = str(dados.cliente_id)+'_'+str(cliente.tx_sigla).replace(' ', '').lower()

            dir_cli_workers = os.getcwd()+'/workers/'+str(tx_sigla)

            os.makedirs(dir_cli_workers, exist_ok=True)

            dir_cliente = dir_cli_workers+'/'+str(dados.tx_nome)+'.zip'
            dir_cliente = dir_cliente.replace('/', '/')

            if os.path.isfile(dir_workers+'/worker-setup.zip'):
                dest = shutil.copy(dir_workers+'/worker-setup.zip', dir_cliente)

            tx_json = json.loads(dados.tx_json)

            tamanho = 8
            valores = string.ascii_letters
            senha = ''
            for i in range(tamanho):
                senha += random.choice(valores)

            senha_hash = await hash_provider.gerar_hash(senha)

            config_json = {
                "url_console": f"{tx_json['url_console']}",
                "username": f"{cpf}",
                "password": f"{senha_hash}",
                "worker": 'WORKER_'+str(dados.tx_nome).upper().replace('@',''),
                "tempo_espera": 10,
                "email": f"{tx_json['tx_email']}"
            }

            db_orm = models.Usuario(
                nu_cpf = cpf,
                tx_nome = 'WORKERS_'+str(dados.tx_nome).upper().replace('@',''),
                tx_email = tx_json['tx_email'],
                tx_senha = senha_hash,
                bo_worker = True
            )
            self.db.add(db_orm)
            self.db.commit()
            
            db_uss = models.UsuarioCliente(
                nu_cpf = cpf,
                cliente_id = dados.cliente_id
            )            
            self.db.add(db_uss)
            self.db.commit()

            db_ormP = models.PerfilUsuario(
                nu_cpf = cpf,
                perfil_id = 4
            )
            self.db.add(db_ormP)
            self.db.commit()

            db_ormA = models.AutomacaoUsuario(
                nu_cpf = dados.nu_cpf,
                automacao_id = dados.id,
                cliente_id = dados.cliente_id
            )
            self.db.add(db_ormA)
            self.db.commit()

            stmt = update(models.Automacao).where(models.Automacao.id == dados.id).values(
                tx_json = str(config_json)
            )
            self.db.execute(stmt)
            self.db.commit()

            config = dotenv_values(".env")
            configJson = json.loads((json.dumps(config) ))
            config_json = {"url_console": f"{configJson['URL_BACK_AUTOMAXIA']}", "worker": 'WORKER_'+str(dados.tx_nome).upper().replace('@','')}

            with ZipFile(dir_cliente, 'a') as myzip:
                #with myzip.open('workers-setup/config.json','r') as myfile:
                with open(str(os.getcwd()).replace('/', '/')+'/worker.json', "a", encoding='utf_8_sig') as outfile:
                    outfile.write(str(config_json).replace("'", '"'))
                myzip.write('workers.json')
                myzip.close()

            if os.path.isfile(str(os.getcwd()).replace('/', '/')+'/worker.json'):
                os.remove(os.getcwd()+'/worker.json')

            filename_s3 = str(dados.tx_nome)+'.zip'
            object_name = f"arquivos/workers/{tx_sigla}/{filename_s3}"
            s3_client = boto3.client('s3', aws_access_key_id=configJson['AWS_ACCESS_KEY_ID'], aws_secret_access_key=configJson['AWS_SECRET_ACCESS_KEY'])
            response = s3_client.upload_file(dir_cliente, configJson['S3_BUCKET'], object_name)

        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {"detail": f"""{traceback.format_exc()}""","data": str(dataErro)}

    async def gravar_worker(self, orm: schemas.Automacao):
        try:
            db_orm = models.Automacao(
                tx_nome = orm.tx_nome.upper(),
                cliente_id = orm.cliente_id,
                tx_descricao = orm.tx_descricao,
                tx_json = orm.tx_json,
                nu_cpf = orm.nu_cpf,
                nu_qtd_tarefa = orm.nu_qtd_tarefa,
                tx_constante_virtual = 'WORKER_'+str(orm.tx_nome.upper()).replace('@','')
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)

            retorno = await self.gerar_worker_cliente(db_orm)
            return await self.get_by_id(db_orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {"detail": f"""{traceback.format_exc()}""","data": str(dataErro)}

    async def post(self, orm: schemas.Automacao):
        try:
            db_orm = models.Automacao(
                tx_nome = orm.tx_nome.upper(),
                cliente_id = orm.cliente_id,
                tx_descricao = orm.tx_descricao,
                bo_status = orm.bo_status,
                tx_json = orm.tx_json
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            #await self.deleteAutomacaoUsuario(ormP.nu_cpf)
            '''db_ormA = models.AutomacaoUsuario(
                automacao_id = db_orm.id,
                nu_cpf = orm.nu_cpf
            )
            self.db.add(db_ormA)

            self.db.commit()
            self.db.refresh(db_orm)'''
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def deleteAutomacaoUsuario(self, nu_cpf: str):
        try:
            stmt = delete(models.AutomacaoUsuario).where(models.AutomacaoUsuario.nu_cpf == nu_cpf)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Automacao):
        try:
            stmt = update(models.Automacao).where(models.Automacao.id == orm.id).values(
                tx_descricao = orm.tx_descricao,
                bo_status = orm.bo_status,
                nu_qtd_tarefa = orm.nu_qtd_tarefa,
                nu_qtd_download = orm.nu_qtd_download,
                tx_json = orm.tx_json
            )
            self.db.execute(stmt)
            self.db.commit()
            
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def delete(self, id: int):
        try:
            stmt = update(models.Automacao).where(models.Automacao.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Registro excluido com sucesso.'}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        