from fastapi import APIRouter, status, Depends, Form, HTTPException, Query
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado
from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.usuario import RepositorioUsuario

from src.providers import hash_provider, token_provider

from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, List, Optional
from fastapi.routing import APIRoute

from fastapi.security import OAuth2PasswordRequestForm

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

router = APIRouter(tags=['Auth'], route_class=RouteErrorHandler)

@router.post("/login", status_code=status.HTTP_200_OK)
async def efetuar_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(get_db)):
    #print('username', form_data.username)
    #print('password', form_data.password)
    #print('client_id', form_data.client_id)
    nu_cpf = form_data.username
    tx_senha = form_data.password
    client_id = form_data.client_id
    #print(nu_cpf, tx_senha, client_id)
    
    usuario = await RepositorioUsuario(db).get_by_id(nu_cpf, True)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'O USUÁRIO informado não encontrado!')
    
    expirar = ''
    if client_id == 'worker':
        expirar = 9000000
        senha_valida = False
        if tx_senha == usuario.tx_senha:
            senha_valida = True
    else:
        senha_valida = await hash_provider.verifica_hash(tx_senha, usuario.tx_senha)
    
    if not senha_valida:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A SENHA informada não encontrada!')

    # Gerando Token JWT
    token = await token_provider.gerar_access_token({'sub': usuario.nu_cpf, 'client_id':client_id}, expirar)

    return schemas.LoginSucesso(usuario=usuario, access_token=token)

@router.post("/me", response_model=schemas.UsuarioSimples)
async def obter_usuario(usuario: schemas.Usuario = Depends(obter_usuario_logado)):
    return usuario