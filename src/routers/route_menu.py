from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.menu import RepositorioMenu

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

@router.get("/menu", tags=['Menu'], status_code=status.HTTP_200_OK, response_model=List[schemas.MenuLista])
async def listar_todos_menus(nu_codigo: Optional[str] = Query(default=None), 
                                tx_nome: Optional[str] = Query(default=None, max_length=20),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioMenu(db).get_all(nu_codigo, tx_nome, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/menu/", tags=['Menu'], status_code=status.HTTP_201_CREATED, response_model=schemas.Menu)
async def inserir_menu(model: schemas.MenuPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioMenu(db).get_menu_by_nome(model.tx_nome)    
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um menu cadastrado com esse Nome: {model.tx_nome} informado!')
    retorno = await RepositorioMenu(db).post(model)
    return retorno

@router.put("/menu/", tags=['Menu'], status_code=status.HTTP_200_OK)
async def atualizar_menu(model: schemas.Menu, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioMenu(db).put(model)
    return retorno

@router.get("/menu/{menu_id}", tags=['Menu'], status_code=status.HTTP_200_OK, response_model=schemas.MenuLista)
async def pegar_menu(menu_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioMenu(db).get_by_id(menu_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {menu_id} informado!')
    return retorno

@router.get("/menu/perfil/{perfil_id}", tags=['Menu'], status_code=status.HTTP_200_OK, response_model=List[schemas.MenuLista])
async def pegar_menu(perfil_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioMenu(db).get_menu_by_perfil(perfil_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {perfil_id} informado!')
    return retorno

@router.delete("/menu/{menu_id}", tags=['Menu'], status_code=status.HTTP_200_OK)
async def apagar_menu(menu_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioMenu(db).delete(menu_id)
    return retorno