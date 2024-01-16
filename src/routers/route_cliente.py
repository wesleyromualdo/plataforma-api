from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.cliente import RepositorioCliente

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

@router.get("/cliente", tags=['Cliente'], status_code=status.HTTP_200_OK, response_model=List[schemas.ClienteLista])
async def listar_todos_clientes(tx_sigla: Optional[str] = Query(default=None, max_length=20),
                                tx_nome: Optional[str] = Query(default=None, max_length=200),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioCliente(db).get_all(tx_sigla, tx_nome, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/cliente/", tags=['Cliente'], status_code=status.HTTP_201_CREATED, response_model=schemas.Cliente)
async def inserir_cliente(model: schemas.ClientePOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCliente(db).get_cliente_by_nome(model.tx_nome)
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um cliente cadastrado com esse Nome: {model.tx_nome} informado!')
    retorno = await RepositorioCliente(db).post(model)
    return retorno

@router.put("/cliente/", tags=['Cliente'], status_code=status.HTTP_200_OK)
async def atualizar_cliente(model: schemas.Cliente, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        retorno = await RepositorioCliente(db).put(model)
        return retorno
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um cliente cadastrado com esse Nome: {model.tx_nome} informado!')
        return {'status': 1, 'message': error}

@router.put("/cliente/ultimo_acesso", tags=['cliente'], status_code=status.HTTP_200_OK)
async def altera_ultimo_acesso_usuario(model: schemas.UsuarioClienteAcesso, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCliente(db).altera_ultimo_acesso_usuario(model)
    return retorno

@router.get("/cliente/{cliente_id}", tags=['Cliente'], status_code=status.HTTP_200_OK, response_model=schemas.ClienteLista)
async def pegar_cliente(cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCliente(db).get_by_id(cliente_id)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {cliente_id} informado!')
    return retorno

@router.get("/cliente/usuario/{nu_cpf}", tags=['Cliente'], status_code=status.HTTP_200_OK)
async def pegar_cliente_usuario(nu_cpf: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCliente(db).get_cliente_by_usuario(nu_cpf)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.delete("/cliente/{cliente_id}", tags=['Cliente'], status_code=status.HTTP_200_OK)
async def apagar_cliente(cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCliente(db).delete(cliente_id)
    return retorno