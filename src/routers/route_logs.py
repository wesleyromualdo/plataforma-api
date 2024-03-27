from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.log import RepositorioLogs

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

@router.get("/logs", tags=['Logs'], status_code=status.HTTP_200_OK, response_model=List[schemas.LogsLista])
async def listar_todos_logs(historico_id: Optional[int] = Query(default=None),
                            tx_descricao: Optional[str] = Query(default=None),
                            pagina: Optional[int] = Query(default=0),
                            tamanho_pagina: Optional[int] = Query(default=0), 
                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioLogs(db).get_all(historico_id, tx_descricao, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/logs/", tags=['Logs'], status_code=status.HTTP_201_CREATED, response_model=schemas.LogsLista)
async def inserir_log(model: schemas.LogsPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    if model.historico_tarefa_id == '' or model.historico_tarefa_id == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O id do histórico da tarefa não encontrado!')
    retorno = await RepositorioLogs(db).post(model)
    return retorno

@router.put("/logs/", tags=['Logs'], status_code=status.HTTP_200_OK, response_model=schemas.LogsLista)
async def atualizar_log(model: schemas.Logs, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).put(model)
    return retorno

@router.get("/logs/{log_id}", tags=['Logs'], status_code=status.HTTP_200_OK, response_model=schemas.LogsLista)
async def pegar_log(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).get_by_id(log_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {log_id} informado!')
    return retorno

@router.get("/logs/historico-tarefa/{historico_tarefa_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def pegar_logs_por_historico_tarefa_id(historico_tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).get_logs_por_historico_id(historico_tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa de id: {historico_tarefa_id} informado!')
    return retorno

@router.delete("/logs/{log_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def apagar_log(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).delete(log_id)
    return retorno

@router.post("/logs/elasticsearch", tags=['Logs'], status_code=status.HTTP_201_CREATED)
async def inserir_doc_elastic(model: schemas.LogsElastic, db: Session = Depends(get_db)):
    retorno = await RepositorioLogs(db).inserir_doc_elastic(model)
    return retorno