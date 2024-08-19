from pyexpat import model
from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz, json, math
from elasticsearch import Elasticsearch

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioLogs():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Logs).where(models.Logs.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, historico_id, tx_descricao, pagina:int, tamanho_pagina:int):
        try:
            result = self.db.query(models.Logs).order_by(models.Logs.id.desc())

            if tx_descricao:
                result = result.filter(models.Logs.tx_descricao.ilike(f"%{tx_descricao}%"))
            
            if historico_id:
                result = result.filter(models.Logs.historico_tarefa_id == historico_id)

            total_registros = result.count()

            if tamanho_pagina > 0:
                result = result.offset(pagina).limit(tamanho_pagina)
            
            
            return {"total": total_registros, "dados": result.all()}
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.Logs):
        try:
            #diretorio_image = utils.salvar_imagem_base64_diretorio(orm.tx_imagem)

            db_orm = models.Logs(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                tx_descricao = orm.tx_descricao,
                tx_json = orm.tx_json,
                tx_imagem = orm.tx_imagem
            )
            
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Logs):
        try:
            #diretorio_image = utils.salvar_imagem_base64_diretorio(orm.tx_imagem)

            stmt = update(models.Logs).where(models.Logs.id == orm.id).values(
                historico_tarefa_id = orm.historico_tarefa_id,
                tx_status = orm.tx_status,
                tx_descricao = orm.tx_descricao,
                tx_json = orm.tx_json,
                tx_imagem = orm.tx_imagem
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
            stmt = delete(models.Logs).where(models.Logs.id == id)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_logs_por_historico_id(self, historico_id: int):
        try:
            stmt = select(models.Logs).where(models.Logs.historico_tarefa_id == historico_id).order_by(models.Logs.id.desc())
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def pegar_relatorio_mensal_historico_tarefa(self, cliente_id, tarefa_id, dt_inicio, dt_fim):
        try:
            filtros = []
            if tarefa_id:
                filtros.append(f" AND t.id = {tarefa_id}")

            sql = f"""SELECT
                            (sum(total_minutos) * 0.30) AS preco_total,
                            CEIL(sum(total_minutos)) AS minutos,
                            CEIL(sum(minutos_sucesso)) AS minutos_sucesso,
                            CEIL(sum(minutos_erro)) AS minutos_erro,
                            sum(execucao_sucesso) AS qtd_execucao_sucesso,
                            sum(execucao_error) AS qtd_execucao_error,
                            sum(execucoes) AS qtd_execucoes,
                            to_char((CASE WHEN sum(execucoes) > 0 THEN (100 * sum(execucao_sucesso)) / sum(execucoes) ELSE 0 END), 'FM999999990.00') AS percentual_sucesso,
                            to_char((CASE WHEN sum(execucoes) > 0 THEN (100 * sum(execucao_error)) / sum(execucoes) ELSE 0 END), 'FM999999990.00') AS percentual_erro,
                            min(total_minutos) AS total_minutes,
                            max(total_minutos) AS maior_tempo,
                            min(total_minutos) AS menor_tempo,
                            TO_CHAR(((sum(total_minutos) ) / sum(execucoes)), 'FM999999999.00') AS tempo_medio_execucao
                        FROM(
                            SELECT th.id AS historico, t.id, t.tx_nome, th.dt_fim::timestamp, th.dt_inicio::timestamp,
                                ROUND(COALESCE(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp)),1)) AS total_segundos,
                                CASE WHEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) > 0 
                                    THEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) ELSE 1 END AS total_minutos,
                                ROUND(CASE WHEN th.bo_status_code >= 200 AND th.bo_status_code <= 299 THEN CASE WHEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) > 0 
                                    THEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) ELSE 1 END ELSE 0 END) AS minutos_sucesso,
                                ROUND(CASE WHEN th.bo_status_code > 299 THEN CASE WHEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) > 0 
                                    THEN ROUND(EXTRACT(EPOCH FROM (th.dt_fim::timestamp - th.dt_inicio::timestamp))/60) ELSE 1 END ELSE 0 END) AS minutos_erro,
                                th.bo_status_code,
                                CASE WHEN th.bo_status_code >= 200 AND th.bo_status_code <= 299 THEN 1 ELSE 0 END execucao_sucesso,
                                CASE WHEN th.bo_status_code > 299 THEN 1 ELSE 0 END execucao_error,
                                count(th.id) AS execucoes
                            FROM public.tarefa_historico th 
                                INNER JOIN public.tarefa t ON t.id = th.tarefa_id
                        WHERE th.dt_inicio BETWEEN to_timestamp('{dt_inicio} 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp('{dt_fim} 23:59:59', 'YYYY-MM-DD HH24:MI:SS')
                            AND t.cliente_id = {cliente_id}
                            AND th.dt_fim IS NOT NULL
                            {''.join(filtros)}
                        GROUP BY th.bo_status_code, th.dt_fim, th.dt_inicio, t.id, t.tx_nome,th.id
                    ) AS foo"""
            
            #resultado = self.db.execute(sql).all()
            
            sql = f"""WITH log_error AS (
                        SELECT historico_tarefa_id FROM public.logs l 
                        WHERE l.tx_status = 'error'
                        GROUP BY historico_tarefa_id
                    ),
                    log_sucesso AS (
                        SELECT historico_tarefa_id FROM public.logs l 
                        WHERE l.tx_status NOT IN ('error')
                            AND l.historico_tarefa_id NOT IN ( SELECT historico_tarefa_id FROM public.logs l 
                                WHERE l.tx_status in ('error'))
                        GROUP BY historico_tarefa_id
                    ),
                    dados_execucao AS (
                        SELECT l.historico_tarefa_id, min(l.dt_inclusao) AS dt_inicio, max(l.dt_inclusao) AS dt_fim,
                            ROUND(COALESCE(EXTRACT(EPOCH FROM (max(l.dt_inclusao)::timestamp - min(l.dt_inclusao)::timestamp)),1)) AS total_segundos,
                            CASE WHEN ROUND(EXTRACT(EPOCH FROM (max(l.dt_inclusao)::timestamp - min(l.dt_inclusao)::timestamp))/60) > 0
                                THEN ROUND(EXTRACT(EPOCH FROM (max(l.dt_inclusao)::timestamp - min(l.dt_inclusao)::timestamp))/60) ELSE 1 
                            END AS total_minutos,
                            CASE WHEN count(ls.historico_tarefa_id) > 0 THEN ROUND(COALESCE(EXTRACT(EPOCH FROM (max(l.dt_inclusao)::timestamp - min(l.dt_inclusao)::timestamp)),1)) ELSE 0 END segundos_sucesso,
                            CASE WHEN count(le.historico_tarefa_id) > 0 THEN ROUND(COALESCE(EXTRACT(EPOCH FROM (max(l.dt_inclusao)::timestamp - min(l.dt_inclusao)::timestamp)),1)) ELSE 0 END segundos_erro,
                            CASE WHEN count(ls.historico_tarefa_id) > 0 THEN 1 ELSE 0 END execucao_sucesso,
                            CASE WHEN count(le.historico_tarefa_id) > 0 THEN 1 ELSE 0 END execucao_error
                        FROM logs l 
                            LEFT JOIN log_sucesso ls ON ls.historico_tarefa_id = l.historico_tarefa_id
                            LEFT JOIN log_error le ON le.historico_tarefa_id = l.historico_tarefa_id
                        --WHERE l.historico_tarefa_id = 6160
                        GROUP BY l.historico_tarefa_id
                    )
                    SELECT th.id AS historico, t.id, t.tx_nome, 
                            de.dt_inicio, de.dt_fim, de.total_segundos, de.segundos_sucesso, de.segundos_erro, de.execucao_sucesso, de.execucao_error,
                            count(th.id) AS execucoes
                        FROM public.tarefa_historico th
                            INNER JOIN public.tarefa t ON t.id = th.tarefa_id
                            INNER JOIN dados_execucao de ON de.historico_tarefa_id = th.id
                    WHERE th.dt_inicio BETWEEN to_timestamp('{dt_inicio} 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp('{dt_fim} 23:59:59', 'YYYY-MM-DD HH24:MI:SS')
                            AND t.cliente_id = {cliente_id}
                            AND th.dt_fim IS NOT NULL
                            {''.join(filtros)}
                            AND th.dt_fim IS NOT NULL
                        GROUP BY th.bo_status_code, th.dt_fim, th.dt_inicio, t.id, t.tx_nome,th.id,
                            de.dt_inicio, de.dt_fim, de.total_segundos, de.segundos_sucesso, de.segundos_erro, de.execucao_sucesso, de.execucao_error"""
            
            db_orm = self.db.execute(sql).all()
            total_minutos = 0
            minutos_sucesso = 0
            minutos_erro = 0
            qtd_execucao_sucesso = 0
            qtd_execucao_error = 0
            qtd_execucoes = 0
            maior_tempo = 0
            menor_tempo = float('inf')
            tempo_total_execucao = 0

            for row in db_orm:
                total_minutos += row['total_segundos']/60
                minutos_sucesso += row['segundos_sucesso'] / 60
                minutos_erro += row['segundos_erro'] / 60
                qtd_execucao_sucesso += row['execucao_sucesso']
                qtd_execucao_error += row['execucao_error']
                qtd_execucoes += row['execucoes']
                tempo_total_execucao += row['total_segundos']
                if row['total_segundos'] > maior_tempo:
                    maior_tempo = row['total_segundos']/60
                if row['total_segundos'] < menor_tempo:
                    menor_tempo = row['total_segundos']/60

            percentual_sucesso = ((qtd_execucao_sucesso / qtd_execucoes) * 10000) / 100 if qtd_execucoes > 0 else 0
            percentual_erro = ((qtd_execucao_error / qtd_execucoes) * 10000) / 100 if qtd_execucoes > 0 else 0
            tempo_medio_execucao = (tempo_total_execucao / qtd_execucoes) / 60 if qtd_execucoes > 0 else 0

            resultado = {
                "preco_total": (float(total_minutos) * 0.30),
                "minutos": float("{:.2f}".format(total_minutos)),
                "minutos_sucesso": float("{:.2f}".format(minutos_sucesso)),
                "minutos_erro": float("{:.2f}".format(minutos_erro)),
                "qtd_execucao_sucesso": qtd_execucao_sucesso,
                "qtd_execucao_error": qtd_execucao_error,
                "qtd_execucoes": qtd_execucoes,
                "percentual_sucesso": "{:.2f}".format(percentual_sucesso),
                "percentual_erro": "{:.2f}".format(percentual_erro),
                "maior_tempo": float("{:.2f}".format(maior_tempo)),
                "menor_tempo": float("{:.2f}".format(menor_tempo)),
                "tempo_medio_execucao": float("{:.2f}".format(tempo_medio_execucao))
            }
                
            return [resultado]
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return error

    async def inserir_doc_elastic(self, orm: schemas.LogsElastic):
        try:

            es = Elasticsearch(["http://elasticsearch.logging.svc.cluster.local:9200"])
            index_name = orm.index_name

            if not es.indices.exists(index=index_name):
                es.indices.create(index=index_name)
            
            res = es.index(index=index_name, body=orm.json_dados)
            return res['result']
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return traceback.format_exc()