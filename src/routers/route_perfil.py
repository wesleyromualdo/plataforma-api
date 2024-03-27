from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.perfil import RepositorioPerfil

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

@router.get("/perfil", tags=['Perfil'], status_code=status.HTTP_200_OK)
async def listar_todos_perfils(tx_nome: Optional[str] = Query(default=None, max_length=20),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioPerfil(db).get_all(tx_nome, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/perfil/", tags=['Perfil'], status_code=status.HTTP_201_CREATED)
async def inserir_perfil(model: schemas.PerfilPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioPerfil(db).get_perfil_by_nome(model.tx_nome)    
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um perfil cadastrado com esse Nome: {model.tx_nome} informado!')
    retorno = await RepositorioPerfil(db).post(model)
    return retorno

@router.put("/perfil/", tags=['Perfil'], status_code=status.HTTP_200_OK)
async def atualizar_perfil(model: schemas.Perfil, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioPerfil(db).put(model)
    return retorno

@router.get("/perfil/{perfil_id}", tags=['Perfil'], status_code=status.HTTP_200_OK, response_model=schemas.PerfilLista)
async def pegar_perfil(perfil_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioPerfil(db).get_by_id(perfil_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {perfil_id} informado!')
    return retorno

@router.get("/perfil/usuario/{nu_cpf}", tags=['Perfil'], status_code=status.HTTP_200_OK)
async def pegar_perfil_usuario(nu_cpf: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioPerfil(db).get_perfil_by_usuario(nu_cpf)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.delete("/perfil/{perfil_id}", tags=['Perfil'], status_code=status.HTTP_200_OK)
async def apagar_perfil(perfil_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioPerfil(db).delete(perfil_id)
    return retorno