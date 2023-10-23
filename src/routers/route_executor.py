from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.executor import RepositorioExecutor

from starlette.requests import Request
from starlette.responses import Response, FileResponse
from typing import Callable
from fastapi.routing import APIRoute
import traceback
from datetime import datetime, date, timezone

import pytz, os
from src.utils import utils

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

@router.get("/executor", tags=['Executor'], status_code=status.HTTP_200_OK)
async def listar_todos(automacao_id: Optional[str] = Query(default=None),
                                setor_id: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    
    retorno = await RepositorioExecutor(db).get_all(automacao_id, setor_id, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/executor/", tags=['Executor'], status_code=status.HTTP_201_CREATED)
async def gravar_download_executor(model: schemas.DownloadExecutorPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    donwload = await RepositorioExecutor(db).get_by_automacao_ipmec(model.tx_ip_mac, model.automacao_id)
    if not donwload:
        donwload = await RepositorioExecutor(db).post(model)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK, detail=f'{donwload.id}')
    return donwload

@router.put("/executor/arquitetura/", tags=['Executor'], status_code=status.HTTP_200_OK)
async def atualiza_dados_executor(model: schemas.DownloadExecutor, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioExecutor(db).atualiza_dados_executor(model)
    return retorno

@router.put("/executor/stop/{executor_id}", tags=['Executor'], status_code=status.HTTP_200_OK)
async def stop_executor(executor_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioExecutor(db).stop_executor(executor_id)
    return retorno

@router.delete("/executor/{executor_id}", tags=['Executor'], status_code=status.HTTP_200_OK)
async def stop_executor(executor_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioExecutor(db).delete(executor_id)
    return retorno