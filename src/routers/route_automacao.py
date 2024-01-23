from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.automacao import RepositorioAutomacao
from src.sqlalchemy.repositorios.cliente import RepositorioCliente

from starlette.requests import Request
from starlette.responses import Response, FileResponse
from typing import Callable
from fastapi.routing import APIRoute
import traceback
from datetime import datetime, date, timezone
import boto3, json

import pytz, os
from src.utils import utils
from dotenv import dotenv_values

AMSP = pytz.timezone('America/Sao_Paulo')

class RouteErrorHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as ex:
                if isinstance(ex, HTTPException):
                    raise ex
                print(ex)
                raise HTTPException(status_code=500, detail=str({'status': 1, 'message': ex}))
        return custom_route_handler

router = APIRouter(route_class=RouteErrorHandler)

@router.get("/automacao", tags=['Automação'], status_code=status.HTTP_200_OK)
async def listar_todas_automacoes(tx_nome: Optional[str] = Query(default=None, max_length=200),
                                cliente_id: Optional[str] = Query(default=None),
                                bo_status: Optional[str] = Query(default=True),
                                nu_cpf: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    
    retorno = await RepositorioAutomacao(db).get_all(cliente_id, tx_nome, bo_status, nu_cpf, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/automacao/", tags=['Automação'], status_code=status.HTTP_201_CREATED, response_model=schemas.Automacao)
async def inserir_automacao(model: schemas.AutomacaoPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_automacao_by_nome(model.tx_nome)    
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um Automacao cadastrado com esse Nome: {retorno.id} - {model.tx_nome} informado!')
    retorno = await RepositorioAutomacao(db).post(model)
    return retorno

@router.post("/automacao/worker/", tags=['Automação'], status_code=status.HTTP_201_CREATED)
async def gravar_worker(model: schemas.AutomacaoPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_automacao_by_nome(model.tx_nome)    
    
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um Automacao cadastrado com esse Nome: {retorno.id} - {model.tx_nome} informado!')
    retorno = await RepositorioAutomacao(db).gravar_worker(model)
    return retorno

@router.put("/automacao/", tags=['Automação'], status_code=status.HTTP_200_OK)
async def atualizar_automacao(model: schemas.Automacao, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).put(model)
    return retorno

@router.get("/automacao/{automacao_id}", tags=['Automação'], status_code=status.HTTP_200_OK, response_model=schemas.AutomacaoLista)
async def pegar_automacao(automacao_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_by_id(automacao_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {automacao_id} informado!')
    return retorno

@router.get("/automacao/worker/{automacao_id}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def pegar_automacao_worker(automacao_id: int, db: Session = Depends(get_db)):
    retorno = await RepositorioAutomacao(db).get_txjson_by_id(automacao_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {automacao_id} informado!')
    return retorno

@router.get("/automacao/worker/constante/{constante_virtual}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def pegar_automacao_worker(constante_virtual: str, db: Session = Depends(get_db)):
    retorno = await RepositorioAutomacao(db).get_txjson_by_constante_virtual(constante_virtual)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a constante_virtual: {constante_virtual} informado!')
    return retorno

@router.get("/automacao/cliente/{cliente_id}", tags=['Automação'], status_code=status.HTTP_200_OK, response_model=List[schemas.Automacao])
async def pegar_automacao_cliente(cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_by_cliente(cliente_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {cliente_id} informado!')
    return retorno

@router.get("/automacao/usuario/{nu_cpf}/{cliente_id}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def pegar_automacao_usuario(nu_cpf: str, cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_automacao_by_usuario(nu_cpf, cliente_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.get("/automacao/worker/{nu_cpf}/{tx_ip_mac}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def get_usuario_by_worker(nu_cpf: str, tx_ip_mac: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_usuario_by_worker(nu_cpf, tx_ip_mac)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.get("/automacao/combodashboard/{nu_cpf}/{cliente_id}/{periodo}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def pegar_automacao_usuario(nu_cpf: str, cliente_id: int, periodo:int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).get_automacao_by_usuario_dashboard(nu_cpf, cliente_id, periodo)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.get("/automacao/aws", tags=['Automação'], status_code=status.HTTP_200_OK)
async def pegar_dados():
    retorno = os.getenv('AWS_CONTAINER_CREDENTIALS_RELATIVE_URI')
    return retorno

@router.delete("/automacao/{automacao_id}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def apagar_automacao(automacao_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAutomacao(db).delete(automacao_id)
    return retorno

@router.get("/download/worker/{automacao_id}", tags=['Automação'], status_code=status.HTTP_200_OK)
async def download_worker(automacao_id: int,db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioAutomacao(db).get_by_id_sql(automacao_id)
        cliente = await RepositorioCliente(db).get_by_id(retorno.cliente_id)
        tx_sigla = str(retorno.cliente_id)+'_'+str(cliente.tx_sigla).replace(' ', '').lower()

        file_name = str(retorno.tx_nome)+'.zip'
        file_path = os.getcwd().replace('\\','/') + "/workers/"+str(tx_sigla)+'/'+ file_name
        file_path_seg = os.getcwd().replace('\\','/') + "/workers/"+str(retorno.cliente_id)+"_automaxia/"+ file_name

        os.makedirs(os.getcwd() + "/workers/"+str(tx_sigla), exist_ok=True)
        
        config = dotenv_values(".env")
        config = json.loads((json.dumps(config) ))
        s3_client = boto3.client('s3', aws_access_key_id=config['AWS_ACCESS_KEY_ID'], aws_secret_access_key=config['AWS_SECRET_ACCESS_KEY'])

        object_name = f"arquivos/workers/{tx_sigla}/{file_name}"
        
        s3_client.download_file(
            Bucket=config['S3_BUCKET'],
            Key=object_name,
            Filename=file_path
        )
        
        if (int(retorno.total_donwload) +1) > int(retorno.nu_qtd_download):
            return {'detail': f'A quantidade permitida de download foi atingida.'}
        #print(file_path)
        if os.path.isfile(file_path):
            arquivo = FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)   
            #if os.path.exists(file_path):
            #    os.remove(file_path)
            return arquivo
        elif os.path.isfile(file_path_seg):
            arquivo = FileResponse(path=file_path_seg, media_type='application/octet-stream', filename=file_name)   
            #if os.path.exists(file_path):
            #    os.remove(file_path)
            return arquivo
        else:
            return {'status': status.HTTP_404_NOT_FOUND, 'detail': f'O arquivo {file_name} não foi encontrado no diretório!'}
            #raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O arquivo {file_name} não foi encontrado no diretório!')
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(error)}