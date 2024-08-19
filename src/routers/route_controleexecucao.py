from fastapi import APIRouter, status, Depends, HTTPException, Query, UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.controleexecucao import RepositorioControleExecucao

from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse
from datetime import datetime, date, timezone
import os, uuid

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
                raise HTTPException(status_code=500, detail=str({'status': 1, 'detail': ex}))
        return custom_route_handler

router = APIRouter(route_class=RouteErrorHandler)

@router.get("/controleexecucao", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def listar_todos(tarefa_id: Optional[str] = Query(default=None),
                                tx_chave: Optional[str] = Query(default=None, max_length=200),
                                tx_descricao: Optional[str] = Query(default=None, max_length=200),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioControleExecucao(db).get_all(tarefa_id, tx_chave, tx_descricao, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.get("/controleexecucao/dash", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def listar_todos(tarefa_id: Optional[str] = Query(default=None),
                       cliente_id: Optional[str] = Query(default=None),
                        tx_chave: Optional[str] = Query(default=None, max_length=200),
                        dt_inicio: Optional[str] = Query(default=None),
                        dt_fim: Optional[str] = Query(default=None), 
                        tx_descricao: Optional[str] = Query(default=None, max_length=200),
                        tx_situacao: Optional[str] = Query(default=None, max_length=50),
                        pagina: Optional[int] = Query(default=0),
                        tamanho_pagina: Optional[int] = Query(default=0), 
                        db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioControleExecucao(db).get_all_by_dash(tarefa_id, cliente_id, tx_chave, dt_inicio, dt_fim, tx_descricao, tx_situacao, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/controleexecucao/", tags=['Controle Execução'], status_code=status.HTTP_201_CREATED, response_model=schemas.ControleExecucao)
async def inserir(model: schemas.ControleExecucaoPOST, db: Session = Depends(get_db)):
    #retorno = await RepositorioControleExecucao(db).get_by_chave(model.tarefa_id, model.tx_chave)
    #if retorno:
    #    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um controle execução cadastrado com esse Nome: {model.tx_descricao} informado!')
    retorno = await RepositorioControleExecucao(db).post(model)
    return retorno

@router.put("/controleexecucao/", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def atualizar(model: schemas.ControleExecucao, db: Session = Depends(get_db)):
    retorno = await RepositorioControleExecucao(db).put(model)
    return retorno

@router.get("/controleexecucao/{tarefa_id}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def pegar_por_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    retorno = await RepositorioControleExecucao(db).get_by_tarefa(tarefa_id)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa id: {tarefa_id} informado!')
    return retorno

@router.get("/controleexecucao/chave/{tarefa_id}/{tx_chave}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def pegar_por_chave(tarefa_id: int, tx_chave:str, db: Session = Depends(get_db)):
    retorno = await RepositorioControleExecucao(db).get_by_chave(tarefa_id, tx_chave)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a chave: {tx_chave} informado!')
    return retorno

@router.get("/controleexecucao/situacao/{tarefa_id}/{tx_situacao}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def pegar_por_situacao(tarefa_id: int, tx_situacao:str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).get_by_situacao(tarefa_id, tx_situacao)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a situação: {tx_situacao} informado!')
    return retorno

@router.delete("/controleexecucao/{tarefa_id}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def apagar_cliente(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).delete(tarefa_id)
    return retorno

@router.get("/controleexecucao/download-image/{controle_id}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def download_imagem(controle_id: int,db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).get_by_id(controle_id)

    file_path = retorno.tx_imgbase64
    file_name = os.path.basename(file_path)
    
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O arquivo {file_name} não foi encontrado no diretório!')
