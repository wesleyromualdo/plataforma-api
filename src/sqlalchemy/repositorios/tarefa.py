from sqlalchemy import select, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
import os, json
import traceback
from datetime import datetime, date, timezone, time
import pytz
from tzlocal import get_localzone
from src.utils import utils

AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioTarefa():

    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, id: int):
        try:
            stmt = select(models.Tarefa).where(models.Tarefa.id == id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_by_constante_virtual(self, constante_virtual: str):
        try:
            stmt = select(models.Tarefa).where(models.Tarefa.tx_constante_virtual == constante_virtual)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def carrega_tarefa_cliente(self, cliente_id: int):
        try:
            stmt = select(models.Tarefa).where(models.Tarefa.cliente_id == cliente_id).where(models.Tarefa.bo_status == True)
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_tarefa_by_automacao_id(self, automacao_id: int):
        try:
            j = join(models.Tarefa, models.Automacao, models.Tarefa.automacao_id == models.Automacao.id)
            stmt = select(models.Tarefa).select_from(j).where(models.Tarefa.automacao_id == automacao_id).where(models.Tarefa.bo_status == True)
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_tarefa_by_nome(self, tx_nome: str, cliente_id: str):
        try:
            stmt = select(models.Tarefa).where(models.Tarefa.tx_nome == tx_nome).where(models.Tarefa.bo_status == True).where(models.Tarefa.cliente_id == cliente_id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, nu_cpf, tx_nome, bo_execucao, bo_status, automacao_id, cliente_id, bo_agendada, pagina=0, tamanho_pagina=0):
        try:
            filtro = ''
            join = ''

            if bo_execucao == True or bo_execucao == False:
                filtro += f" and t.bo_execucao = {bo_execucao}"

            if bo_agendada is not None and ('true' in str(bo_agendada) or 'false' in str(bo_agendada)):
                filtro += f" and t.bo_agendada = {bo_agendada}"

            if nu_cpf:
                join += "INNER JOIN automacao_usuario au ON t.automacao_id = au.automacao_id"
                filtro += f" and au.nu_cpf = '{nu_cpf}'"

            if automacao_id:
                filtro += f" and t.automacao_id = {automacao_id}"

            filtro_tmp = ''
            if cliente_id:
                filtro += f" and t.cliente_id = {cliente_id}"
                filtro_tmp += f" and t.cliente_id = {cliente_id}"

            if tx_nome:
                filtro += f" and t.tx_nome ilike '%{tx_nome}%'"

            sql = f"""WITH historico AS (
                        SELECT tarefa_id, dt_fim, dt_inicio FROM tarefa_historico th
							INNER JOIN tarefa t ON t.id = th.tarefa_id AND t.historico_id = th.id
						WHERE t.bo_status = TRUE {filtro_tmp} --AND dt_fim IS NOT NULL AND th.automacao_id IS NOT NULL
                    )
                    SELECT DISTINCT 
                        t.id, t.automacao_id, t.nu_cpf, t.tx_nome, t.tx_situacao, t.dt_inclusao, t.bo_status, t.cliente_id, t.bo_execucao, t.bo_agendada, 
                        t.json_agendamento, t.tx_assunto_inicia, t.tx_corpo_email_inicia, t.tx_assunto_finaliza, t.tx_corpo_email_finaliza, t.bo_email, t.historico_id, 
                        a.tx_nome AS automacao, t.tx_json, th.dt_inicio, th.dt_fim, '' as agendamento, t.anexo_script_id, t.nu_prioridade
                    FROM tarefa t
                        INNER JOIN automacao a ON a.id = t.automacao_id 
                        {join}
                        LEFT JOIN historico th ON th.tarefa_id = t.id
                    WHERE t.bo_status = {bo_status} {filtro}
                    order by th.dt_fim DESC, t.id"""
            
            result = self.db.execute(sql).all()
            
            if bo_agendada is not None and 'true' in str(bo_agendada):
                result = await self.carrega_coluna_agendamento(result)
            return result
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def carrega_coluna_agendamento(self, resultado):
        try:
            utc_dt = datetime.now(timezone.utc)

            data = utc_dt.astimezone(AMSP).strftime("%Y-%m-%d")
            hora = utc_dt.astimezone(AMSP).strftime("%H:%M")
            horas = hora.split(':')

            data_formatada = utc_dt.astimezone(AMSP).strftime("%d/%m/%Y")
            dataDate = datetime.strptime(data, "%Y-%m-%d").date()
            arDados = []        
            resultado = self.transformaDict(resultado)

            for result in resultado:
                if result['bo_agendada'] is True and result['json_agendamento'] != '' and result['json_agendamento'] is not None:
                    result['agendamento'] = '-'
                    try:
                        agendamento = json.loads(result['json_agendamento'])
                        dataFim = datetime.strptime(agendamento['datafim'], "%Y-%m-%d").date()

                        if agendamento['repetir'] == True:
                            dataFim = dataDate

                        if agendamento['cronograma'] == 'diario':
                            if agendamento['repetirhora'] == True and dataFim >= dataDate:
                                result['agendamento'] = data_formatada+' às '+str(int(horas[0])+1)+':00'
                            else:
                                for agenda in agendamento['agenda']:
                                    #if int(agenda.split(':')[0]) >= int(horas[0]) and dataFim >= dataDate:
                                    if time(int(horas[0]), int(horas[1])) < time(int(agenda.split(':')[0]), int(agenda.split(':')[1])) and dataFim >= dataDate:
                                        result['agendamento'] = data_formatada+' às '+agenda
                                        break
                        if agendamento['cronograma'] == 'semanal':
                            if 'agenda' not in agendamento:
                                return False

                            retorno = self.verifica_dia_semana(agendamento)
                            if retorno[0] is True:
                                agenda = retorno[1]
                                result['agendamento'] = self.trata_semana(agenda['semana'])+' às '+agenda['hora'][0]
                            else:
                                result['agendamento'] = agendamento['agenda'][0]['semana']+' às '+agendamento['agenda'][0]['hora'][0]

                        if agendamento['cronograma'] == 'mensal':
                            if 'agenda' not in agendamento:
                                return False

                            for agenda in agendamento['agenda']:
                                mensal = datetime.strptime(agenda['mensal'], "%Y-%m-%d").date()
                                if mensal >= dataDate:
                                    result['agendamento'] = mensal.strftime("%d/%m/%Y")+' às '+agenda['hora'][0]
                                    break                    
                    except Exception as error:
                        utc_dt = datetime.now(timezone.utc)
                        dataErro = utc_dt.astimezone(AMSP)
                        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
                        return {'detail': str(traceback.format_exc())}
                arDados.append(result)
            return arDados
        except:
            print(traceback.format_exc())
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    def trata_semana(self, semana):
        nomes = [{"SEG":"SEGUNDA"}, {"TER":"TERÇA"}, {"QUA":"QUARTA"}, {"QUI":"QUINTA"}, {"SEX":"SEXTA"}, {"SAB":"SÁBADO"}, {"DOM":"DOMINGO"}]
        
        for nome in nomes:
            for n in nome:
                if semana == n:
                    return nome[n]

    def verifica_dia_semana(self, agendamento):
        dia_semana = date.today().weekday()
        nomes = ["SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM"]

        for agenda in agendamento['agenda']:
            for k, v in enumerate(nomes):
                if v == agenda['semana']:
                    if k >= dia_semana and k < 6: 
                        return True, agenda
                        break
        return [False, ]

    def transformaDict(self, results):
        return [dict(r) for r in results]

    async def carrega_tarefa_dashboard_grafico(self, cliente_id, automacao_id, periodo, nu_cpf):
        try:
            
            filtro = ''
            if automacao_id:
                filtro = f" AND t.automacao_id = {automacao_id} "

            stmt = f"""SELECT DISTINCT dt_inicio_formatada, to_char(dt_inicio_formatada::timestamp, 'DD/MM/YYYY') as dt_inicio 
                        FROM(
                            SELECT to_char(th.dt_inicio::timestamp, 'YYYY-MM-DD') AS dt_inicio_formatada
                            FROM tarefa t
                                INNER JOIN cliente s ON s.id = t.cliente_id
                                INNER JOIN tarefa_historico th ON th.tarefa_id = t.id
                                INNER JOIN automacao_usuario au ON au.automacao_id = t.automacao_id
                            WHERE t.cliente_id = {cliente_id}
                                {filtro}
                                AND th.dt_inicio BETWEEN (now() - INTERVAL '{periodo} day') AND now()
                                AND au.nu_cpf = '{nu_cpf}'
                        ) AS foo
                        ORDER BY foo.dt_inicio_formatada;"""
            db_data = self.db.execute(stmt).all()

            registros = []
            datas = []
            for data in db_data:
                data_inicio = data.dt_inicio_formatada
                datas.append(data.dt_inicio)
                stmt = f"""WITH tarefa_by_id AS (
                                SELECT DISTINCT t.id AS tarefa_id
                                FROM tarefa t
                                    INNER JOIN cliente s ON s.id = t.cliente_id
                                    INNER JOIN automacao_usuario au ON au.automacao_id = t.automacao_id
                                    INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.dt_inicio BETWEEN (now() - INTERVAL '{periodo} day') AND now()
                                WHERE t.cliente_id = {cliente_id}
                                    AND au.nu_cpf = '{nu_cpf}'
                                    AND t.bo_status = TRUE
                                    {filtro}
                            )
                            SELECT 
                                automacao_id,
                                tarefa,
                                cliente,
                                automacao,
                                COALESCE(dt_inicio, to_char('{data_inicio}'::timestamp, 'DD/MM/YYYY')) AS dt_inicio,
                                CASE WHEN dt_inicio IS NULL THEN 'N' ELSE 'S' END AS tem_historico,
                                COALESCE(sum(tempo)::time, '00:00:00'::time) AS tempo_total,
                                COALESCE(DATEDIFF('minute', '1900-01-01 00:00:00'::timestamp, ('1900-01-01 '||sum(tempo)::time)::timestamp),0) AS minutos
                            FROM(
                                SELECT t.id AS tarefa_id, a.id AS automacao_id, t.tx_nome AS tarefa, s.tx_sigla AS cliente, a.tx_nome AS automacao,
                                    to_char(th.dt_inicio::timestamp, 'DD/MM/YYYY') AS dt_inicio, th.dt_fim::timestamp, (th.dt_fim::timestamp - th.dt_inicio::timestamp)::time AS tempo
                                FROM tarefa t
                                    INNER JOIN automacao a ON a.id = t.automacao_id
                                    INNER JOIN cliente s ON s.id = t.cliente_id
                                    INNER JOIN automacao_usuario au ON au.automacao_id = t.automacao_id
                                    LEFT JOIN tarefa_historico th ON th.tarefa_id = t.id AND to_char(th.dt_inicio, 'YYYY-MM-DD') = '{data_inicio}'
                                WHERE t.cliente_id = {cliente_id}
                                    AND t.bo_status = TRUE
                                    AND t.id IN (SELECT tarefa_id FROM tarefa_by_id)
                                    AND au.nu_cpf = '{nu_cpf}'
                                    {filtro}
                            ) AS foo
                            GROUP BY tarefa, cliente, automacao, dt_inicio, automacao_id
                            ORDER BY dt_inicio;"""
            
                db_orm = self.db.execute(stmt).all()
                registros.append({'data':data.dt_inicio, 'registros':db_orm})
            return registros
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def carrega_dados_automacao_dashboard(self, cliente_id, automacao_id, periodo):
        try:
            filtro = ''
            if automacao_id:
                filtro = f" AND t.automacao_id = {automacao_id} "
            
            stmt = f"""SELECT 
                            sum(execucao) AS execucao,
                            sum(finalizada) AS finalizada,
                            sum(ativas) AS ativas,
                            sum(inativas) AS inativas,
                            to_char(now(), 'YYYY-MM-DD')||' '||sum(tempo_total) AS tempo_total,
                            sum(segundos) AS total_segundos,
                            0 as tempo
                        FROM(
                            SELECT DISTINCT a.tx_nome AS automacao, 
                                CASE WHEN t.bo_execucao = TRUE THEN 1 ELSE 0 END AS execucao,
                                CASE WHEN t.bo_execucao = FALSE THEN 1 ELSE 0 END AS finalizada,
                                CASE WHEN a.bo_status = TRUE THEN 1 ELSE 0 END AS ativas,
                                CASE WHEN a.bo_status = FALSE THEN 1 ELSE 0 END AS inativas,
                                th.tempo_total,
                                th.segundos
                            FROM tarefa t 
                                INNER JOIN automacao a ON a.id = t.automacao_id
                                LEFT JOIN(
                                    SELECT tarefa_id, sum(th.dt_fim::timestamp - th.dt_inicio::timestamp)::time AS tempo_total,
                                        sum(DATEDIFF('second', th.dt_inicio::timestamp, th.dt_fim::timestamp)) AS segundos 
                                    FROM tarefa_historico th
                                    WHERE th.dt_inicio BETWEEN (now() - INTERVAL '{periodo} day') AND now()
                                    GROUP BY tarefa_id
                                ) th ON th.tarefa_id = t.id 
                            WHERE a.bo_status = TRUE
                                AND t.bo_status = TRUE
                                AND t.cliente_id = {cliente_id}
                                {filtro}
                        ) AS foo;"""
            db_orm = self.db.execute(stmt).first()

            if db_orm.total_segundos is None:
                return {
                    'ativas': '0',
                    'execucao': '0',
                    'finalizada': '0',
                    'inativas': '0',
                    'tempo' : '0',
                    'tempo_total': '',
                    'total_segundos': '0'
                },{
                    'dias':0,
                    'horas':0,
                    'minutos':0,
                    'segundos':0
                }
            
            segundos = int(db_orm.total_segundos)

            dias, segundos = divmod(segundos, 86400)
            horas, segundos = divmod(segundos, 3600)
            minutos, segundos = divmod(segundos, 60)
            
            tempo = {
                'dias':dias,
                'horas':horas,
                'minutos':minutos,
                'segundos':segundos
            }
            return db_orm,tempo
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_historico_tarefa_by_usuario(self, nu_cpf: str, bo_agendada: bool):
        try:
            filtro = ''
            if bo_agendada is not None:
                filtro = f' AND t.bo_agendada = {bo_agendada}'

            stmt = f"""SELECT DISTINCT th.id, th.tarefa_id, th.nu_cpf, th.dt_inicio, th.dt_fim, th.bo_status_code, th.tx_resumo, th.tx_json
                    FROM tarefa t
                        INNER JOIN cliente s ON s.id = t.cliente_id AND s.bo_status = true
                        INNER JOIN tarefa_historico th ON th.tarefa_id = t.id --AND th.id = t.historico_id
                        INNER JOIN automacao_usuario au ON au.automacao_id = t.automacao_id
                    WHERE t.bo_status = TRUE
                        AND au.nu_cpf = '{nu_cpf}'
                        {filtro}
                        --AND th.id = (SELECT max(id) AS id FROM tarefa_historico WHERE tarefa_id = th.tarefa_id)
                    ORDER BY th.tarefa_id"""
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_historico_tarefa_by_tarefa_all(self, tarefa_id: int, historico_id:int, dt_inicio:str, pagina:str, tamanho_pagina:str):
        try:
            #stmt = select(models.TarefaHistorico).where(models.TarefaHistorico.tarefa_id == tarefa_id).order_by(models.TarefaHistorico.id.desc())
            #db_orm = self.db.execute(stmt).scalars().all()

            total_registros = 10
            if pagina != '':
                total_sql = f"""SELECT COUNT(th.id) FROM tarefa_historico th 
                            WHERE th.tarefa_id = {tarefa_id}
                                {f"AND to_char(th.dt_inicio, 'DD/MM/YYYY às HH24:MI:SS') ILIKE '%{dt_inicio}%'" if dt_inicio != '' else ""}"""
                
                total_registros = self.db.execute(total_sql).scalars().first()

            sql = f"""SELECT th.*, a.tx_nome as worker FROM tarefa_historico th 
                        LEFT JOIN automacao a ON a.id = th.automacao_id 
                    WHERE th.tarefa_id = {tarefa_id}
                        {f"AND to_char(th.dt_inicio, 'DD/MM/YYYY às HH24:MI:SS') ILIKE '%{dt_inicio}%'" if dt_inicio != '' else ""}
                        {f"AND th.id = {historico_id}" if historico_id != '' else ""}
                    ORDER BY th.id DESC
                    {f"OFFSET {int(pagina) * int(tamanho_pagina)} ROWS FETCH NEXT {int(tamanho_pagina)} ROWS ONLY" if pagina != '' else ""}"""
            
            db_orm = self.db.execute(sql).all()
            return {"total": total_registros, "dados": db_orm}
        except:
            print(traceback.format_exc())
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_historico_tarefa_by_tarefa_id(self, tarefa_id: int):
        try:
            stmt = select(models.TarefaHistorico).where(models.TarefaHistorico.tarefa_id == tarefa_id).order_by(models.TarefaHistorico.id.desc())
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_historico_tarefa_by_historico_id(self, historico_id: int):
        try:
            stmt = select(models.TarefaHistorico).where(models.TarefaHistorico.id == historico_id)
            db_orm = self.db.execute(stmt).scalars().first()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_tarefahistorico_by_automacao(self, automacao_id: int):
        try:
            stmt = f"""SELECT t.tx_nome, th.dt_inicio, th.dt_fim, th.nu_cpf, u.tx_nome as usuario
                    FROM tarefa t 
                        INNER JOIN tarefa_historico th ON th.tarefa_id = t.id
                        INNER JOIN usuario u ON u.nu_cpf  = th.nu_cpf 
                    WHERE t.bo_status = TRUE
                        AND t.automacao_id = {automacao_id}
                    ORDER BY th.id DESC;"""
            db_orm = self.db.execute(stmt).all()
            
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_automacao_tarefa_by_id(self, automacao_id: int):
        try:
            #await self.verifica_agendamento_tarefa(automacao_id)
            
            j = join(models.Automacao, models.Tarefa, models.Tarefa.automacao_id == models.Automacao.id)
            #stmt = select(models.Cliente).select_from(j).where(models.UsuarioCliente.nu_cpf == nu_cpf)

            stmt = select(models.Tarefa, models.Automacao.tx_json).select_from(j).where(models.Tarefa.automacao_id == automacao_id).where(models.Tarefa.bo_execucao == True)
            db_orm = self.db.execute(stmt).first()
            if not db_orm:
                return db_orm
            db_orm1 = db_orm.Tarefa
            db_orm1.tx_json = db_orm.tx_json
            
            return db_orm1
        except Exception as erro:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    #async def verifica_agendamento_tarefa(self, automacao_id: int):
    async def verifica_agendamento_tarefa(self, nu_cpf='', nome_worker='', automacao_id = '', tarefa_id = '', bo_iniciar_tarefa = True):
        try:
            today = date.today()

            filtros = []
            if automacao_id and automacao_id is not None:
                filtros.append(f"a.id = {automacao_id}")
            if tarefa_id and tarefa_id is not None:
                filtros.append(f"t.id = {tarefa_id}")
            if nome_worker:
                filtros.append(f"a.tx_ip_mac = '{nome_worker}'")
            if nu_cpf:
                filtros.append(f"au.nu_cpf = '{nu_cpf}'")

            sql = f"""SELECT DISTINCT t.id AS tarefa_id, t.cliente_id, t.automacao_id, t.nu_cpf, t.tx_json, t.bo_agendada, t.json_agendamento,
                    COALESCE(DATEDIFF('second', th.dt_fim::timestamp, now()::timestamp),0) AS segundos,
                    COALESCE(DATEDIFF('hour', th.dt_fim::timestamp, now()::timestamp),0) AS horas
                FROM tarefa t  
                    INNER JOIN automacao a ON a.id = t.automacao_id
                    INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                    LEFT JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.id = t.historico_id
                WHERE t.json_agendamento IS NOT NULL
                    {f"AND {' AND '.join(filtros)}" if len(filtros) > 0 else ""}
                    AND t.json_agendamento != ''
                    AND t.bo_status = TRUE
                    AND t.bo_execucao = FALSE;"""            
            artarefas = self.db.execute(sql).all()
            
            retorno = False
            for tarefas in artarefas:
                if tarefas is not None and tarefas['bo_agendada'] is True and tarefas['segundos'] > 60 and tarefas['json_agendamento'] is not None:
                    try:
                        agendamento = json.loads(tarefas['json_agendamento'])
                    except Exception as error:
                        utc_dt = datetime.now(timezone.utc)
                        dataErro = utc_dt.astimezone(AMSP)
                        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
                        #return {'detail': 'Converter json do agendamento: '+str(traceback.format_exc())}
                    
                    if (int(tarefas['segundos']) < 1 or int(tarefas['segundos']) > 59):
                        if (agendamento['repetir'] is False or agendamento['repetir'] == 'false') and str(today) == agendamento['datafim']:
                            retorno = await self.verifica_tipo_agendamento(tarefas, agendamento)
                        else:
                            if (agendamento['repetir'] is True or agendamento['repetir'] == 'true'):
                                retorno = await self.verifica_tipo_agendamento(tarefas, agendamento)

                    if retorno is True and bo_iniciar_tarefa is True:
                        await self.iniciar_tarefa(tarefas)                    
            return retorno
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def verifica_tipo_agendamento(self, tarefa, agendamento):
        if agendamento['cronograma'] == 'diario':
            return await self.agendamento_diario(tarefa, agendamento)

        if agendamento['cronograma'] == 'semanal':
            return await self.agendamento_semanal(tarefa, agendamento)

        if agendamento['cronograma'] == 'mensal':
            return await self.agendamento_mensal(tarefa, agendamento)

    async def agendamento_diario(self, tarefa, agendamento):
        try:
            utc_dt = datetime.now(timezone.utc)

            data = datetime.strptime(utc_dt.astimezone(AMSP).strftime("%Y-%m-%d"), "%Y-%m-%d")
            hora = utc_dt.astimezone(AMSP).strftime("%H:%M")
            #print(hora, agendamento['agenda'])
            if 'agenda' not in agendamento:
                return {'detail': 'Atributo inválido: agenda - '+str(agendamento)}
            
            #if (agendamento['repetirhora'] is True or agendamento['repetirhora'] == 'true') and (tarefa['horas'] > 0 or str(hora[-2:]) == '00'):
            if (agendamento['repetirhora'] is True or agendamento['repetirhora'] == 'true') and tarefa['horas'] > 0:
                if hora in agendamento['agenda']:
                    return True
            else:
                if (agendamento['repetir'] is True or agendamento['repetir'] == 'true'):
                    if hora in agendamento['agenda']:
                        return True
                else:
                    datafim = datetime.strptime(agendamento['datafim'], "%Y-%m-%d")
                    if hora in agendamento['agenda'] and data == datafim:
                        return True
            return False
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return False

    async def agendamento_semanal(self, tarefa, agendamento):
        try:
            utc_dt = datetime.now(timezone.utc)

            data = datetime.strptime(utc_dt.astimezone(AMSP).strftime("%Y-%m-%d"), "%Y-%m-%d")
            hora = utc_dt.astimezone(AMSP).strftime("%H:%M")

            dia_semana = date.today().weekday()
            nomes = ("SEG", "TER", "QUA", "QUI", "SEX", "SAB", "DOM")

            if 'agenda' not in agendamento:
                return False
            for agenda in agendamento['agenda']:
                #if (agendamento['repetir'] is True or agendamento['repetir'] == 'true') and tarefa['horas'] > 0:
                if (agendamento['repetir'] is True or agendamento['repetir'] == 'true'):
                    if agenda['semana'] == nomes[dia_semana] and hora in agenda['hora']:
                        return True
                else:
                    datafim = datetime.strptime(agendamento['datafim'], "%Y-%m-%d")
                    if agenda['semana'] == nomes[dia_semana] and hora in agenda['hora'] and data == datafim:
                        return True
            return False
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def agendamento_mensal(self, tarefa, agendamento):
        try:
            utc_dt = datetime.now(timezone.utc)

            data = datetime.strptime(utc_dt.astimezone(AMSP).strftime("%Y-%m-%d"), "%Y-%m-%d")
            hora = utc_dt.astimezone(AMSP).strftime("%H:%M")            

            if 'agenda' not in agendamento:
                return False 

            for agenda in agendamento['agenda']:
                datafim = datetime.strptime(agenda['mensal'], "%Y-%m-%d")
                if (agendamento['repetir'] is True or agendamento['repetir'] == 'true'):
                    if hora in agenda['hora']:
                        return True
                else:
                    if datafim == data and hora in agenda['hora']:
                        return True
            return False
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def pega_automacao_espera(self, automacao_id:int, cliente_id:int):
        sql = f"""WITH historico AS (
                    SELECT count(id) AS tarefa, automacao_id, tx_ip_execucao 
                    FROM tarefa_historico WHERE dt_fim IS NULL AND automacao_id IS NOT NULL
                    GROUP BY automacao_id, tx_ip_execucao
                )
                SELECT COALESCE(th.tarefa,0) AS tarefa, de.* FROM download_worker de
                    LEFT JOIN historico th ON th.automacao_id = de.automacao_id AND th.tx_ip_execucao = de.tx_ip_mac
                WHERE de.automacao_id = {automacao_id}
                    and de.cliente_id = {cliente_id}
                    AND de.bo_status = TRUE
                    AND de.bo_ativo = TRUE
                ORDER BY COALESCE(th.tarefa,0) ASC"""
        
        db_orm = self.db.execute(sql).first()
        return db_orm

    async def iniciar_tarefa(self, orm: schemas.IniciaTarefa):
        try:
            tx_ip_mac = ''
            tx_situacao = 'Aguardando'
            if orm.execucao == 'manual' and orm.execucao is not None:
                tx_ip_mac = orm.tx_ip_mac
                tx_situacao = 'Em Execução'
            
            if (tx_ip_mac == '' or tx_ip_mac is None) and orm.cliente_id is not None and orm.automacao_id is not None:
                automacao = await self.pega_automacao_espera(orm.automacao_id, orm.cliente_id)
                tx_ip_mac = automacao.tx_ip_mac

            utc_dt = datetime.now(timezone.utc)
            dt_inicio = utc_dt.astimezone(AMSP)

            db_orm = models.TarefaHistorico(
                tarefa_id = orm.tarefa_id,
                automacao_id = orm.automacao_id,
                nu_cpf = orm.nu_cpf,
                tx_ip_execucao = tx_ip_mac,
                dt_inicio = dt_inicio,
                tx_json = orm.tx_json
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.tarefa_id).values(
                bo_execucao = True,
                historico_id = db_orm.id,
                tx_json = orm.tx_json,
                tx_situacao = tx_situacao
            )
            self.db.execute(stmt)
            self.db.commit()

            tarefa = await self.get_by_id(orm.tarefa_id)

            if tarefa.bo_email is True and tarefa.tx_assunto_inicia  != '' and tarefa.tx_corpo_email_inicia != '' and tarefa.tx_assunto_inicia is not None and tarefa.tx_corpo_email_inicia is not None and tarefa.nu_cpf != '':
                stmt = select(models.Usuario).where(models.Usuario.nu_cpf == tarefa.nu_cpf)
                db_orm_user = self.db.execute(stmt).scalars().first()

                self.envio_email(tarefa.tx_assunto_inicia, tarefa.tx_corpo_email_inicia, db_orm_user.tx_email)

            return tarefa
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return str(error)

    async def parar_tarefa(self, orm: schemas.TarefaHistorico):
        try:
            utc_dt = datetime.now(timezone.utc)
            dt_fim = utc_dt.astimezone(AMSP)

            historico = await self.get_historico_tarefa_by_tarefa_id(orm.tarefa_id)
            stmt = update(models.TarefaHistorico).where(models.TarefaHistorico.id == historico.id).values(
                dt_fim = dt_fim,
                bo_status_code = orm.bo_status_code,
                tx_resumo = orm.tx_resumo
            )
            self.db.execute(stmt)
            self.db.commit()

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.tarefa_id).values(
                bo_execucao = False,
                tx_situacao = 'Finalizada'
            )
            self.db.execute(stmt)
            self.db.commit()

            tarefa = await self.get_by_id(orm.tarefa_id)

            if tarefa.bo_email is True and tarefa.tx_assunto_finaliza != '' and tarefa.tx_corpo_email_finaliza != '' and tarefa.tx_assunto_finaliza is not None and tarefa.tx_corpo_email_finaliza is not None and tarefa.nu_cpf != '':
                stmt = select(models.Usuario).where(models.Usuario.nu_cpf == tarefa.nu_cpf)
                db_orm_user = self.db.execute(stmt).scalars().first()

                self.envio_email(tarefa.tx_assunto_finaliza, tarefa.tx_corpo_email_finaliza, db_orm_user.tx_email)
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def grava_historico_tarefa(self, orm: schemas.TarefaHistoricoPOST):
        try:
            automacao = await self.pega_automacao_espera(orm.automacao_id)
            
            db_orm = models.TarefaHistorico(
                tarefa_id = orm.tarefa_id,
                automacao_id = orm.automacao_id,
                nu_cpf = orm.nu_cpf,
                tx_ip_execucao = automacao.tx_ip_mac,
                tx_json = orm.tx_json
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.tarefa_id).values(
                historico_id = db_orm.id
            )
            self.db.execute(stmt)
            self.db.commit()
            
            return db_orm
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def post(self, orm: schemas.Tarefa):
        try:
            utc_dt = datetime.now(timezone.utc)
            dt_alteracao = utc_dt.astimezone(AMSP)
            db_orm = models.Tarefa(
                tx_nome = orm.tx_nome,
                nu_cpf = orm.nu_cpf,
                cliente_id = orm.cliente_id,
                automacao_id = orm.automacao_id,
                bo_execucao = orm.bo_execucao,
                bo_agendada = orm.bo_agendada,
                bo_status = orm.bo_status,
                bo_email = orm.bo_email,
                tx_nome_script = orm.tx_nome_script,
                tx_situacao = 'Criada',
                nu_prioridade = orm.nu_prioridade,
                tx_constante_virtual = orm.tx_constante_virtual,
                dt_alteracao = dt_alteracao
            )
            self.db.add(db_orm)
            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put(self, orm: schemas.Tarefa):
        try:
            utc_dt = datetime.now(timezone.utc)

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                tx_nome = orm.tx_nome,
                nu_cpf = orm.nu_cpf,
                automacao_id = orm.automacao_id,
                bo_status = orm.bo_status,
                bo_execucao = orm.bo_execucao,
                bo_agendada = orm.bo_agendada,
                bo_email = orm.bo_email,
                tx_nome_script = orm.tx_nome_script,
                nu_prioridade = orm.nu_prioridade,
                tx_constante_virtual = orm.tx_constante_virtual,
                dt_alteracao = utc_dt.astimezone(AMSP)
            )
            self.db.execute(stmt)
            self.db.commit()

            if orm.bo_agendada is False:
                orm.json_agendamento = None
                await self.put_agendamento(orm)

            if orm.bo_alterou_automacao is True:
                self.db.execute(update(models.AnexoScript).where(models.AnexoScript.id == orm.anexo_script_id).values(
                        dt_download = None
                    )
                )
                self.db.commit()

            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put_json_tarefa(self, orm: schemas.Tarefa):
        try:
            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                tx_json = orm.tx_json
            )
            self.db.execute(stmt)
            self.db.commit()

            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put_situacao_tarefa(self, orm: schemas.Tarefa):
        try:

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                tx_situacao = orm.tx_situacao
            )
            self.db.execute(stmt)
            self.db.commit()

            return orm #await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def put_agendamento(self, orm: schemas.Tarefa):
        try:
            utc_dt = datetime.now(timezone.utc)

            stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                json_agendamento = orm.json_agendamento
            )
            self.db.execute(stmt)
            self.db.commit()

            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def config_email_tarefa(self, orm: schemas.Tarefa):
        try:
            if orm.tipo == 'I':
                stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                    tx_assunto_inicia = orm.tx_assunto_inicia,
                    tx_corpo_email_inicia = orm.tx_corpo_email_inicia
                )
            else:
                stmt = update(models.Tarefa).where(models.Tarefa.id == orm.id).values(
                    tx_assunto_finaliza = orm.tx_assunto_finaliza,
                    tx_corpo_email_finaliza = orm.tx_corpo_email_finaliza
                )
            self.db.execute(stmt)
            self.db.commit()
            return await self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def atualiza_historico_tarefa(self, orm: schemas.TarefaHistorico):
        try:
            stmt = update(models.TarefaHistorico).where(models.TarefaHistorico.id == orm.id).values(
                tarefa_id = orm.tarefa_id,
                nu_cpf = orm.nu_cpf,
                automacao_id = orm.automacao_id,
                dt_inicio = orm.dt_inicio,
                dt_fim = orm.dt_fim,
                bo_status_code = orm.bo_status_code,
                tx_ip_execucao = orm.tx_ip_execucao,
                tx_resumo = orm.tx_resumo,
                tx_json = orm.tx_json
            )
            self.db.execute(stmt)
            self.db.commit()
            
            return self.get_by_id(orm.id)
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def atualiza_historico_tarefa_txjson(self, orm: schemas.TarefaHistorico):
        try:
            stmt = update(models.TarefaHistorico).where(models.TarefaHistorico.id == orm.id).values(
                tarefa_id = orm.tarefa_id,
                tx_json = orm.tx_json
            )
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return traceback.format_exc()

    async def delete(self, id: int):
        try:
            stmt = update(models.Tarefa).where(models.Tarefa.id == id).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'detail': 'Registro excluido com sucesso.'}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'detail': error}

    def envio_email(self, subject, html_corpo, email_user):
        import pathlib
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        import smtplib
        

        try:
            json_config = utils.pega_dados_configuracao()
            fromaddr = json_config['config_email']['fromaddr']
            password = json_config['config_email']['password']
            toaddr = email_user
            host = json_config['config_email']['host']
            port = json_config['config_email']['port']
            msg = MIMEMultipart()
            
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = subject

            body = html_corpo

            msg.attach(MIMEText(body, 'html'))

            #dir_atual = os.getcwd()

            #filename = "Registro_Atividade_" + str(date.today()) + '.csv'
            #arquivolog = [fr'{dir_atual}\logs\{filename}']                        

            '''for f in arquivolog:
                attachment = open(f, 'rb')
                part = MIMEBase('application', 'octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                #part.add_header('Content-Disposition',"attachment; filename= %s" % filename)
                part.add_header('Content-Disposition','attachment; filename="%s"'% os.path.basename(f))

                msg.attach(part)
                attachment.close()'''

            server = smtplib.SMTP(host, port)
            server.starttls()
            server.login(fromaddr, password)
            text = msg.as_string()
            toaddrs = [toaddr]
            retorno = server.sendmail(fromaddr, toaddrs, text)
            server.quit()
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def carrega_tarefa_by_cpf(self, nu_cpf, nome_worker):
        try:
            await self.verifica_agendamento_tarefa(nu_cpf, nome_worker)

            stmt = f"""SELECT DISTINCT t.id, t.automacao_id, t.nu_cpf, t.tx_nome, t.bo_status, t.cliente_id, t.bo_execucao, t.bo_agendada, 
                            t.json_agendamento, t.tx_assunto_inicia, t.tx_corpo_email_inicia, t.tx_assunto_finaliza, t.tx_corpo_email_finaliza, t.anexo_script_id,
                            t.bo_email, t.historico_id, t.tx_nome_script, a.tx_ip_mac, t.tx_json AS json_tarefa, to_char(s.dt_inclusao, 'YYYY-MM-DD HH24:MI:SS') as dt_inclusao,
                            to_char(s.dt_download, 'YYYY-MM-DD HH24:MI:SS') as dt_download, t.nu_prioridade
                        FROM tarefa t 
                            INNER JOIN automacao a ON a.id = t.automacao_id 
                            INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                            INNER JOIN anexo_script s ON s.id = t.anexo_script_id AND s.bo_status = TRUE
                            INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.dt_fim IS NOT NULL
                        WHERE /*au.nu_cpf = '{nu_cpf}'
                            AND*/ a.tx_ip_mac = '{nome_worker}'
                            AND t.bo_execucao = TRUE
                        ORDER BY t.nu_prioridade DESC"""
            
            db_data = self.db.execute(stmt).all()
            return db_data
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def carrega_tarefa_by_worker_constante(self, constante_virtual, tx_ip_mac):
        try:
            sql = f"""SELECT de.automacao_id, de.id FROM download_worker de
                        INNER JOIN automacao a ON a.id = de.automacao_id 
                    WHERE a.tx_constante_virtual = '{constante_virtual}' AND de.bo_status = TRUE AND de.tx_ip_mac = '{tx_ip_mac}'"""
            worker = self.db.execute(sql).first()
            
            if worker.automacao_id:
                sql = f"UPDATE download_worker SET dt_alive = now(), bo_ativo = TRUE WHERE id = '{worker.id}'"
                self.db.execute(sql)
                self.db.commit()

                automacao_id = worker.automacao_id
                await self.verifica_agendamento_tarefa('', '', automacao_id)

                stmt = f"""SELECT DISTINCT t.id, t.automacao_id, t.nu_cpf, t.tx_nome, t.bo_status, t.cliente_id, t.bo_execucao, t.bo_agendada, 
                                t.json_agendamento, t.tx_assunto_inicia, t.tx_corpo_email_inicia, t.tx_assunto_finaliza, t.tx_corpo_email_finaliza, t.anexo_script_id,
                                t.bo_email, t.historico_id, t.tx_nome_script, t.tx_json AS json_tarefa, to_char(s.dt_inclusao, 'YYYY-MM-DD HH24:MI:SS') as dt_inclusao,
                                to_char(s.dt_download, 'YYYY-MM-DD HH24:MI:SS') as dt_download, t.nu_prioridade, a.tx_json
                            FROM tarefa t 
                                INNER JOIN automacao a ON a.id = t.automacao_id 
                                INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                                INNER JOIN anexo_script s ON s.id = t.anexo_script_id AND s.bo_status = TRUE
                                INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.dt_fim IS NULL
                            WHERE a.id = '{automacao_id}'
                                and th.tx_ip_execucao = '{tx_ip_mac}'
                                AND t.bo_status = TRUE
                                AND t.bo_execucao = TRUE
                            ORDER BY t.nu_prioridade DESC"""
                
                db_data = self.db.execute(stmt).all()
                return db_data
            else:
                return 'inativo'
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
    
    async def carrega_tarefa_by_worker(self, automacao_id, tx_ip_mac):
        try:
            sql = f"SELECT bo_status, id FROM download_worker WHERE automacao_id = {automacao_id} AND tx_ip_mac = '{tx_ip_mac}'"
            worker = self.db.execute(sql).first()
            
            if worker['bo_status'] is True:
                sql = f"UPDATE download_worker SET dt_alive = now(), bo_ativo = TRUE WHERE id = {worker['id']}"
                self.db.execute(sql)
                self.db.commit()

                await self.verifica_agendamento_tarefa('', '', automacao_id)

                stmt = f"""SELECT DISTINCT t.id, t.automacao_id, t.nu_cpf, t.tx_nome, t.bo_status, t.cliente_id, t.bo_execucao, t.bo_agendada, 
                                t.json_agendamento, t.tx_assunto_inicia, t.tx_corpo_email_inicia, t.tx_assunto_finaliza, t.tx_corpo_email_finaliza, t.anexo_script_id,
                                t.bo_email, t.historico_id, t.tx_nome_script, t.tx_json AS json_tarefa, to_char(s.dt_inclusao, 'YYYY-MM-DD HH24:MI:SS') as dt_inclusao,
                                to_char(s.dt_download, 'YYYY-MM-DD HH24:MI:SS') as dt_download, t.nu_prioridade, a.tx_json
                            FROM tarefa t 
                                INNER JOIN automacao a ON a.id = t.automacao_id 
                                INNER JOIN automacao_usuario au ON au.automacao_id = a.id 
                                INNER JOIN anexo_script s ON s.id = t.anexo_script_id AND s.bo_status = TRUE
                                INNER JOIN tarefa_historico th ON th.tarefa_id = t.id AND th.dt_fim IS NULL
                            WHERE a.id = '{automacao_id}'
                                and th.tx_ip_execucao = '{tx_ip_mac}'
                                AND t.bo_status = TRUE
                                AND t.bo_execucao = TRUE
                            ORDER BY t.nu_prioridade DESC"""
                
                db_data = self.db.execute(stmt).all()
                return db_data
            else:
                return 'inativo'
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        