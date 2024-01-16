from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.cofre_senha import RepositorioCofreSenha
from src.providers import hash_cofresenha

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

@router.get("/cofresenha", tags=['Cofre Senha'], status_code=status.HTTP_200_OK, response_model=List[schemas.CofreSenhaLista])
async def listar_todos(cliente_id: Optional[int] = Query(default=None),
                                tx_nome: Optional[str] = Query(default=None, max_length=300),
                                tx_usuario: Optional[str] = Query(default=None, max_length=50),
                                bo_status: Optional[str] = Query(default=None),
                                pagina: Optional[int] = Query(default=0),
                                tamanho_pagina: Optional[int] = Query(default=0), 
                                db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioCofreSenha(db).get_all(cliente_id, tx_nome, tx_usuario, bo_status, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/cofresenha/", tags=['Cofre Senha'], status_code=status.HTTP_201_CREATED, response_model=schemas.CofreSenhaLista)
async def inserir(model: schemas.CofreSenhaPOST, db: Session = Depends(get_db)):
    retorno = await RepositorioCofreSenha(db).get_by_nome(model.tx_nome, model.cliente_id)
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um cofre de senha cadastrado com esse Nome: {model.tx_nome} informado!')

    model.tx_senha = await hash_cofresenha.gerar_hash(model.tx_senha)
    retorno = await RepositorioCofreSenha(db).post(model)
    return retorno

@router.put("/cofresenha/", tags=['Cofre Senha'], status_code=status.HTTP_200_OK)
async def atualizar(model: schemas.CofreSenha, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    try:
        model.tx_senha = await hash_cofresenha.gerar_hash(model.tx_senha)
        retorno = await RepositorioCofreSenha(db).put(model)
        return retorno
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um cofre de senha cadastrado com esse Nome: {model.tx_descricao} informado!')

@router.get("/cofresenha/{tx_nome}/{cliente_id}", tags=['Cofre Senha'], status_code=status.HTTP_200_OK, response_model=schemas.CofreSenhaLista)
async def pegar_por_nome(tx_nome:str, cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCofreSenha(db).get_by_nome(tx_nome, cliente_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o nome: {tx_nome} informado!')
    
    retorno.tx_senha = await hash_cofresenha.decripta_hash(retorno.tx_senha)
    return retorno

@router.get("/cofresenha/{cliente_id}", tags=['Cofre Senha'], status_code=status.HTTP_200_OK, response_model=schemas.CofreSenhaLista)
async def pegar_por_cliente(cliente_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCofreSenha(db).get_by_cliente(cliente_id)
    
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o cliente id: {cliente_id} informado!')
    return retorno

@router.delete("/cofresenha/{cofresenha_id}", tags=['Cofre Senha'], status_code=status.HTTP_200_OK)
async def apagar_cofresenha(cofresenha_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioCofreSenha(db).delete(cofresenha_id)
    return retorno