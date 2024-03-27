from fastapi import APIRouter, status, Depends, HTTPException, Query, File, UploadFile, WebSocket, WebSocketDisconnect
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.tarefa import RepositorioTarefa
from src.sqlalchemy.repositorios.anexo_script import RepositorioAnexoScript
from src.sqlalchemy.repositorios.cliente import RepositorioCliente

from src.providers.connection_manager import ConnectionManager

from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import FileResponse
from typing import Callable
from fastapi.routing import APIRoute
import traceback
from datetime import datetime, date, timezone
import pytz, os, json
from src.utils import utils
from dotenv import dotenv_values
import boto3, botocore, requests
import logging

AMSP = pytz.timezone('America/Sao_Paulo')

class RouteErrorHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as ex:
                logging.error(f"An error occurred: {ex}")
                if isinstance(ex, HTTPException):
                    raise ex
                raise HTTPException(status_code=500, detail=str({'status': 1, 'detail': str(ex)}))
        return custom_route_handler

router = APIRouter(route_class=RouteErrorHandler)

@router.get("/tarefa", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def listar_todas_tarefas(bo_execucao: Optional[bool] = Query(default=False),
                                nu_cpf: Optional[str] = Query(default=None, max_length=20),
                                tx_nome: Optional[str] = Query(default=None, max_length=200),
                                bo_status: Optional[bool] = Query(default=True),
                                automacao_id: Optional[str] = Query(default=None),
                                cliente_id: Optional[int] = Query(default=None),
                                bo_agendada: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioTarefa(db).get_all(nu_cpf, tx_nome, bo_execucao, bo_status, automacao_id, cliente_id, bo_agendada, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.get("/tarefa/dashboard", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def carrega_tarefa_dashboard(cliente_id: int,
                                automacao_id: Optional[str] = Query(default=None),
                                periodo: Optional[str] = Query(default='10'),
                                nu_cpf: Optional[str] = Query(default=None, max_length=20),
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioTarefa(db).carrega_tarefa_dashboard_grafico(cliente_id, automacao_id, periodo, nu_cpf)
    return retorno

@router.get("/tarefa/dashboard/dados-automacao", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def carrega_dados_automacao_dashboard(cliente_id: int,
                                            automacao_id: Optional[str] = Query(default=None),
                                            periodo: Optional[str] = Query(default='10'), 
                                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).carrega_dados_automacao_dashboard(cliente_id, automacao_id, periodo)
    return retorno

@router.post("/tarefa/", tags=['Tarefa'], status_code=status.HTTP_201_CREATED)
async def inserir_tarefa(model: schemas.TarefaPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).get_tarefa_by_nome(model.tx_nome, model.cliente_id)
        if retorno:
            return {'detail':f'Já existe um Tarefa cadastrado com esse Nome: {model.tx_nome} informado!'}
            #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um Tarefa cadastrado com esse Nome: {model.tx_nome} informado!')

        '''tarefa = await RepositorioTarefa(db).get_tarefa_by_automacao_id(model.automacao_id)        
        if len(tarefa) > 50:
            return {'detail':f'O worker selecionado, já atingiu o número máximo de tarefas vinculadas a ele!'}
            #raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe uma Tarefa({model.tx_nome}) cadastrada para essa automação!')'''
        
        retorno = await RepositorioTarefa(db).post(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(error)}

@router.put("/tarefa/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def atualizar_tarefa(model: schemas.Tarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        '''tarefa = await RepositorioTarefa(db).get_tarefa_by_automacao_id(model.automacao_id)
        if len(tarefa) > 50:
            return {'detail':f'O worker selecionado, já atingiu o número máximo de tarefas vinculadas a ele!'}'''

        retorno = await RepositorioTarefa(db).put(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.put("/tarefa/json_tarefa/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def atualizar_tarefa_json(model: schemas.Tarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).put_json_tarefa(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.put("/tarefa/agendamento/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def atualizar_tarefa_agendamento(model: schemas.Tarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).put_agendamento(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.put("/tarefa/situacao/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def atualiza_situacao_tarefa(model: schemas.Tarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).put_situacao_tarefa(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.put("/tarefa/email/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def configurar_email_tarefa(model: schemas.Tarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).config_email_tarefa(model)
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

@router.post("/tarefa/start/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def iniciar_tarefa(model: schemas.IniciaTarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        if model.tarefa_id == '' or model.tarefa_id is None or model.tarefa_id == 0 or model.nu_cpf == '' or model.nu_cpf is None or model.nu_cpf == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'É necessário o ID da tarefa é o numero do CPF!')
        
        retorno = await RepositorioTarefa(db).get_by_id(model.tarefa_id)
        if model.cliente_id is None:
            model = retorno
            model.tarefa_id = retorno.id
            model.execucao = ''

        if retorno.anexo_script_id is None:
            return {'status': 0, 'message': f"A tarefa {retorno.tx_nome} não foi encontrado script anexado!", 'id':''}
        elif retorno.bo_execucao is True:
            return {'status': 0, 'message': f"A tarefa {retorno.tx_nome} já está em execução. Tente novamente mais tarde.", 'id':retorno.historico_id}
        else:
            if model.execucao == 'manual':
                retorno = await RepositorioTarefa(db).iniciar_tarefa(model)
                return {'status': 1, 'message': 'Iniciando a execução da tarefa manualmente', 'id':retorno.historico_id}
            else:
                automacao = await RepositorioTarefa(db).pega_automacao_espera(model.automacao_id, model.cliente_id)
                if automacao is None:
                    return {'status': 0, 'message': 'Não foi encontrado nenhum worker ativo'}
                else:
                    retorno = await RepositorioTarefa(db).iniciar_tarefa(model)
                    return {'status': 1, 'message': 'Iniciando a execução da tarefa', 'id':retorno.historico_id}
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'status': 0, 'detail': str(error)}
    

@router.put("/tarefa/stop/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def parar_tarefa(model: schemas.StopTarefa, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        if model.tarefa_id == '' or model.tarefa_id is None or model.tarefa_id == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'O código da tarefa é necessário!')

        retorno = await RepositorioTarefa(db).get_by_id(model.tarefa_id)
        if retorno.bo_execucao is True:
            retorno = await RepositorioTarefa(db).parar_tarefa(model)
            return {'status': 1, 'detail': 'Finalizando a execução da tarefa'}
        else:
            return {'status': 0, 'detail': f"A tarefa {retorno.tx_nome} já está finalizada. Tente novamente mais tarde."}
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'status': 0, 'detail': error}

@router.get("/tarefa/{tarefa_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK, response_model=schemas.TarefaLista)
async def pegar_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_by_id(tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {tarefa_id} informado!')
    return retorno

@router.get("/tarefa/constante_virtual/{constante_virtual}", tags=['Tarefa'], status_code=status.HTTP_200_OK, response_model=schemas.TarefaLista)
async def pegar_tarefa_by_constante_virtual(constante_virtual: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_by_constante_virtual(constante_virtual)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a constante virtual: {constante_virtual} informado!')
    return retorno

@router.get("/tarefa/historico/{tarefa_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_historico_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_historico_tarefa_by_tarefa_all(tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa de id: {tarefa_id} informado!')
    return retorno

@router.get("/tarefa/historico_by_usuario/{nu_cpf}/{bo_agendada}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_historico_tarefa_por_usuario(nu_cpf: str, bo_agendada: Optional[bool] = Query(default=None), db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_historico_tarefa_by_usuario(nu_cpf, bo_agendada)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a cpf: {nu_cpf} informado!')
    return retorno

@router.get("/tarefa/historico-tarefa/{historico_tarefa_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_historico_tarefa_por_id(historico_tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_historico_tarefa_by_historico_id(historico_tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa de id: {historico_tarefa_id} informado!')
    return retorno

@router.post("/historico-tarefa/", tags=['Tarefa'], status_code=status.HTTP_200_OK, response_model=schemas.TarefaHistoricoLista)
async def grava_historico_tarefa(model: schemas.TarefaHistoricoPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).grava_historico_tarefa(model)
    return retorno

@router.put("/tarefa/historico-tarefa/", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def atualiza_historico_tarefa(model: schemas.TarefaHistorico, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).atualiza_historico_tarefa(model)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa de id: {historico_tarefa_id} informado!')
    return retorno

@router.get("/tarefa/historico/automacao/{automacao_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_tarefahistorico_automacao(automacao_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).get_tarefahistorico_by_automacao(automacao_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a automação: {automacao_id} informado!')
    return retorno

@router.get("/tarefa/automacao/{automacao_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_automacao_tarefa(automacao_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).get_automacao_tarefa_by_id(automacao_id)        
        if not retorno:
            return {'detail': f'Não foi encontrado nenhuma tarefa liberada para esta automação de id: {automacao_id}!'}
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhuma tarefa liberada para esta automação de id: {automacao_id}!')
        else:
            historico = await RepositorioTarefa(db).get_historico_tarefa_by_tarefa_id(retorno.id)
        
            retorno.historico_tarefa_id = ''
            if historico:
                retorno.historico_tarefa_id = historico.id
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(traceback.format_exc())}

@router.get("/tarefa/worker/{automacao_id}/{tx_ip_mac}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def pegar_tarefa_por_worker(automacao_id: int, tx_ip_mac:str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).carrega_tarefa_by_worker(automacao_id, tx_ip_mac)
        if retorno == 'inativo':
            return {'detail': f'Este worker está inativado de ip mac: {tx_ip_mac}!'}

        if not retorno:
            return {'detail': f'Não foi encontrado nenhuma tarefa liberada para esta automação de id: {automacao_id}!'}
        return retorno
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(traceback.format_exc())}

@router.delete("/tarefa/{tarefa_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def apagar_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioTarefa(db).delete(tarefa_id)
    return retorno

@router.get("/tarefa/usuario/{nu_cpf}/{nome_worker}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def carrega_tarefas_por_usuario(nu_cpf: Optional[str] = Query(default=None, max_length=20), nome_worker: Optional[str] = Query(default=None),
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioTarefa(db).carrega_tarefa_by_cpf(nu_cpf, nome_worker)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o n° de CPF informado!')
    return retorno

@router.post("/uploadScripts/{tarefa_id}/{nu_cpf}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def uploadScripts(file: UploadFile, tarefa_id: str, nu_cpf: str, db: Session = Depends(get_db)):
    try:
        from zipfile import ZipFile

        tx_nome = file.filename
        tx_extensao = file.content_type.split('/')[1]
        tx_tipo = file.content_type

        tarefa = await RepositorioTarefa(db).get_by_id(tarefa_id)
        cliente = await RepositorioCliente(db).get_by_id(tarefa.cliente_id)
        tx_sigla = str(cliente.id)+'_'+str(cliente.tx_sigla).replace(' ', '').lower()
        
        contents = file.file.read()
        #diretorio = f"{os.getcwd()}/automacoes/{tx_sigla}/"
        diretorio = f"/data/plataforma/automacoes/{str(tx_sigla)}/"
        os.makedirs(diretorio, exist_ok=True)

        with open(diretorio+file.filename, 'wb') as f:
            f.write(contents)

        config = dotenv_values(".env")
        config = json.loads((json.dumps(config) ))

        '''filename_s3 = file.filename
        object_name = f"arquivos/automacoes/{tx_sigla}/{filename_s3}"
        response = requests.get(f"http://169.254.170.2{os.getenv('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI')}")
        #/v2/credentials/65b80715-ac9d-4752-88b3-b927bc830a6f
        if response.status_code == 200:
            data = response.json()
            session = boto3.Session(
                aws_access_key_id=data['AccessKeyId'],
                aws_secret_access_key=data['SecretAccessKey'],
                aws_session_token=data['Token']
            )

            event_bridge_client = session.client('events')
            lambda_client = session.client('lambda')
            s3_client = session.client('s3')
        
            link = f"{config['URL_S3']}/{tx_sigla}/{filename_s3}"
            #s3_client = boto3.client('s3', aws_access_key_id=config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])

            #s3_client.upload_fileobj(file.file._file, config['S3_BUCKET'], object_name)
            #utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            response = s3_client.upload_file(diretorio+file.filename, config['S3_BUCKET'], object_name)
            #s3_client = boto3.client('s3', aws_access_key_id=data['AccessKeyId'], aws_secret_access_key=data['SecretAccessKey'])
        else:
            return {'status': response.status_code, 'detail': f'Não conectou no AWS'}'''

        file_stats = os.stat(diretorio+file.filename)
        size = file_stats.st_size
        power = 2**10
        n = 0
        #power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        
        #nu_tamanho = f"{size:,.2f} "+power_labels[n]
        nu_tamanho = f"{size:,.2f}"
        
        nu_arquivo = ''
        if 'zip' in tx_extensao:
            z = ZipFile(diretorio+file.filename, 'r')
            nu_arquivo = len(z.infolist())

        json_anexo:schemas.AnexoScriptPOST = schemas.AnexoScriptPOST(
            tarefa_id=tarefa_id,
            tx_nome=tx_nome,
            tx_extensao=tx_extensao,
            tx_tipo=tx_tipo,
            nu_tamanho=nu_tamanho,
            nu_arquivo=nu_arquivo,
            nu_cpf=nu_cpf
        )

        diretorio = diretorio+file.filename
        file.file.close()
        try:
            if os.path.exists(diretorio):
                os.remove(diretorio)
        except:
            print('')

        await RepositorioAnexoScript(db).post(json_anexo)
        return {"detail": f"Successfully uploaded {file.filename}", "arquivo":f"{os.getcwd()}"}
        
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(error)}
    #finally:
    #    file.file.close()
    #    return {"detail": f"Successfully uploaded {file.filename}", "arquivo":f"{file.filename}"}

@router.get("/downloadScripts/{tarefa_id}", tags=['Tarefa'], status_code=status.HTTP_200_OK)
async def downloadScripts(tarefa_id: int,db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioTarefa(db).get_by_id(tarefa_id)

        cliente = await RepositorioCliente(db).get_by_id(retorno.cliente_id)
        tx_sigla = str(cliente.id)+'_'+str(cliente.tx_sigla).replace(' ', '').lower()

        file_name = retorno.tx_nome_script
        #file_path = os.getcwd() + "/file_path/"+str(tx_sigla)+'/'+ file_name
        file_path = f"/data/plataforma/automacoes/"+str(tx_sigla)+'/'+ file_name

        #os.makedirs(os.getcwd() + "/automacoes/"+str(tx_sigla), exist_ok=True)

        '''config = dotenv_values(".env")
        config = json.loads((json.dumps(config) ))
        s3_client = boto3.client('s3', aws_access_key_id=config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])

        object_name = f"arquivos/automacoes/{tx_sigla}/{file_name}"
        
        s3_client.download_file(
            Bucket=config['S3_BUCKET'],
            Key=object_name,
            Filename=file_path
        )'''
        
        await RepositorioAnexoScript(db).put(retorno.anexo_script_id)
        if os.path.isfile(file_path):
            return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O arquivo {file_name} não foi encontrado no diretório!')

    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(traceback.format_exc())}

'''import random
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print('Accepting client connection...')
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")'''
