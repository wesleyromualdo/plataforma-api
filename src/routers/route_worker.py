from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.worker import RepositorioWorker

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

@router.get("/worker", tags=['Worker'], status_code=status.HTTP_200_OK)
async def listar_todos(automacao_id: Optional[str] = Query(default=None),
                                cliente_id: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    
    retorno = await RepositorioWorker(db).get_all(automacao_id, cliente_id, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/worker/", tags=['Worker'], status_code=status.HTTP_201_CREATED)
async def gravar_download_worker(model: schemas.DownloadWorkerPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    donwload = await RepositorioWorker(db).get_by_automacao_ipmec(model.tx_ip_mac, model.automacao_id)
    if not donwload:
        donwload = await RepositorioWorker(db).post(model)
    else:
        raise HTTPException(status_code=status.HTTP_200_OK, detail=f'{donwload.id}')
    return donwload

@router.put("/worker/arquitetura/", tags=['Worker'], status_code=status.HTTP_200_OK)
async def atualiza_dados_worker(model: schemas.DownloadWorker, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioWorker(db).atualiza_dados_worker(model)
    return retorno

@router.put("/worker/stop/{worker_id}", tags=['Worker'], status_code=status.HTTP_200_OK)
async def stop_worker(worker_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioWorker(db).stop_worker(worker_id)
    return retorno

@router.delete("/worker/{worker_id}", tags=['Worker'], status_code=status.HTTP_200_OK)
async def delete_worker(worker_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioWorker(db).delete(worker_id)
    return retorno