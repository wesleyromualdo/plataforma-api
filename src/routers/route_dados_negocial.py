from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.dados_negocial import RepositorioDadosNegocial

from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from fastapi.routing import APIRoute
from src.utils import utils
import traceback
from datetime import datetime

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

@router.get("/dadosnegocial", tags=['DadosNegocial'], status_code=status.HTTP_200_OK, response_model=List[schemas.DadoNegocialLista])
async def listar_todos_dados_negociais(historico_id: Optional[int] = Query(default=None), 
                            tx_descricao: Optional[str] = Query(default=''),
                            tx_status: Optional[str] = Query(default=''),
                            pagina: Optional[int] = Query(default=0),
                            tamanho_pagina: Optional[int] = Query(default=0), 
                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioDadosNegocial(db).get_all(historico_id, tx_descricao, tx_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/dadosnegocial/", tags=['DadosNegocial'], status_code=status.HTTP_201_CREATED)
async def inserir_dados_negocial(model: schemas.DadoNegocialPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioDadosNegocial(db).post(model)
        return retorno
    except:
        print(traceback.format_exc())
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(datetime.now())})

@router.put("/dadosnegocial/", tags=['DadosNegocial'], status_code=status.HTTP_200_OK, response_model=schemas.DadoNegocialLista)
async def atualizar_dados_negocial(model: schemas.DadoNegocial, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioDadosNegocial(db).put(model)
    return retorno

@router.get("/dadosnegocial/{log_id}", tags=['DadosNegocial'], status_code=status.HTTP_200_OK, response_model=schemas.DadoNegocialLista)
async def pegar_dados_negocial(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioDadosNegocial(db).get_by_id(log_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {log_id} informado!')
    return retorno

@router.delete("/dadosnegocial/{log_id}", tags=['DadosNegocial'], status_code=status.HTTP_200_OK, response_model=schemas.DadoNegocialLista)
async def apagar_dados_negocial(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioDadosNegocial(db).delete(log_id)
    return retorno