from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.setor import RepositorioSetor

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

@router.get("/setor", tags=['Setor'], status_code=status.HTTP_200_OK, response_model=List[schemas.SetorLista])
async def listar_todos_setores(tx_sigla: Optional[str] = Query(default=None, max_length=20),
                                tx_nome: Optional[str] = Query(default=None, max_length=200),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioSetor(db).get_all(tx_sigla, tx_nome, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/setor/", tags=['Setor'], status_code=status.HTTP_201_CREATED, response_model=schemas.Setor)
async def inserir_setor(model: schemas.SetorPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioSetor(db).get_setor_by_nome(model.tx_nome)
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um setor cadastrado com esse Nome: {model.tx_nome} informado!')
    retorno = await RepositorioSetor(db).post(model)
    return retorno

@router.put("/setor/", tags=['Setor'], status_code=status.HTTP_200_OK)
async def atualizar_setor(model: schemas.Setor, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioSetor(db).put(model)
        return retorno
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um setor cadastrado com esse Nome: {model.tx_nome} informado!')
        return {'status': 1, 'message': error}

@router.put("/setor/ultimo_acesso", tags=['Setor'], status_code=status.HTTP_200_OK)
async def altera_ultimo_acesso_usuario(model: schemas.UsuarioSetorAcesso, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioSetor(db).altera_ultimo_acesso_usuario(model)
    return retorno

@router.get("/setor/{setor_id}", tags=['Setor'], status_code=status.HTTP_200_OK, response_model=schemas.SetorLista)
async def pegar_setor(setor_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioSetor(db).get_by_id(setor_id)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {setor_id} informado!')
    return retorno

@router.get("/setor/usuario/{nu_cpf}", tags=['Setor'], status_code=status.HTTP_200_OK)
async def pegar_setor_usuario(nu_cpf: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioSetor(db).get_setor_by_usuario(nu_cpf)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.delete("/setor/{setor_id}", tags=['Setor'], status_code=status.HTTP_200_OK)
async def apagar_setor(setor_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioSetor(db).delete(setor_id)
    return retorno