from fastapi import APIRouter, status, Depends, HTTPException, Query
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

@router.get("/controleexecucao", tags=['Controle Execução'], status_code=status.HTTP_200_OK, response_model=List[schemas.ControleExecucaoLista])
async def listar_todos(tarefa_id: Optional[int] = Query(default=None),
                                tx_descricao: Optional[str] = Query(default=None, max_length=200),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioControleExecucao(db).get_all(tarefa_id, tx_descricao, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/controleexecucao/", tags=['Controle Execução'], status_code=status.HTTP_201_CREATED, response_model=schemas.ControleExecucao)
async def inserir(model: schemas.ControleExecucaoPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).get_by_nome(model.tx_descricao)
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um controle execução cadastrado com esse Nome: {model.tx_descricao} informado!')
    retorno = await RepositorioControleExecucao(db).post(model)
    return retorno

@router.put("/controleexecucao/", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def atualizar(model: schemas.ControleExecucao, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioControleExecucao(db).put(model)
        return retorno
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um controle execução cadastrado com esse Nome: {model.tx_descricao} informado!')

@router.get("/controleexecucao/{tarefa_id}", tags=['Controle Execução'], status_code=status.HTTP_200_OK, response_model=schemas.ControleExecucaoLista)
async def pegar_por_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).get_by_tarefa(tarefa_id)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa id: {tarefa_id} informado!')
    return retorno

@router.delete("/controleexecucao/{tarefa_id}", tags=['Controle Execução'], status_code=status.HTTP_200_OK)
async def apagar_cliente(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioControleExecucao(db).delete(tarefa_id)
    return retorno