from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.configuracao import RepositorioConfiguracao

from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from fastapi.routing import APIRoute

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

@router.get("/configuracao", tags=['Configuração'], status_code=status.HTTP_200_OK)
async def listar_todos(tx_nome: Optional[str] = Query(default=None, max_length=20),
                                tarefa_id: Optional[int] = Query(default=None),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioConfiguracao(db).get_all(tx_nome, tarefa_id, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/configuracao/", tags=['Configuração'], status_code=status.HTTP_201_CREATED)
async def inserir(model: schemas.ConfiguracaoPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioConfiguracao(db).get_configuracao_by_chave(model.tx_chave)    
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um chave cadastrada com esse Nome: {model.tx_chave} informado!')
    retorno = await RepositorioConfiguracao(db).post(model)
    return retorno

@router.put("/configuracao/", tags=['Configuração'], status_code=status.HTTP_200_OK)
async def atualizar(model: schemas.Configuracao, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioConfiguracao(db).put(model)
    return retorno

@router.get("/configuracao/{id}", tags=['Configuração'], status_code=status.HTTP_200_OK, response_model=schemas.ConfiguracaoLista)
async def pegar_configuracao(id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioConfiguracao(db).get_by_id(id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {id} informado!')
    return retorno

@router.get("/configuracao/{tx_chave}", tags=['Configuração'], status_code=status.HTTP_200_OK)
async def pegar_configuracao_chave(tx_chave: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioConfiguracao(db).get_configuracao_by_chave(tx_chave)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a chave: {tx_chave} informada!')
    return retorno

@router.delete("/configuracao/{id}", tags=['Configuração'], status_code=status.HTTP_200_OK)
async def apagar(id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioConfiguracao(db).delete(id)
    return retorno