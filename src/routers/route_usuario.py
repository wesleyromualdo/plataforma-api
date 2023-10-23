from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.usuario import RepositorioUsuario
from src.providers import hash_provider

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

router = APIRouter(tags=['Usuário'], route_class=RouteErrorHandler)
#@router.get('/dados')
#def listar_dados(usuario: schemas.Usuario = Depends(obter_usuario_logado), db: Session = Depends(get_db)):

@router.get("/usuario", status_code=status.HTTP_200_OK)
async def listar_todos_usuario(nu_cpf: Optional[str] = Query(default=''),
                            tx_nome: Optional[str] = Query(default=None, max_length=200),
                            setor_id: Optional[int] = Query(default=None),
                            bo_status: Optional[str] = Query(default=None),
                            pagina: Optional[int] = Query(default=0),
                            tamanho_pagina: Optional[int] = Query(default=0),
                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    return await RepositorioUsuario(db).get_all(nu_cpf, tx_nome, setor_id, bo_status, pagina, tamanho_pagina)

@router.post("/usuario/", status_code=status.HTTP_201_CREATED)
async def inserir_usuario(model: schemas.UsuarioPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioUsuario(db).get_by_id(model.nu_cpf)
    if retorno:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'Já existe um usuário cadastrado com esse CPF: {model.nu_cpf} informado!')
    #model.tx_senha = hash_provider.gerar_hash(model.tx_senha)
    retorno = await RepositorioUsuario(db).post(model)
    return retorno

@router.post("/usuario/dados-acesso/", status_code=status.HTTP_201_CREATED)
async def dados_acesso(model: schemas.DadosAcessoUsuario, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioUsuario(db).dados_acesso(model)
    return retorno    

@router.put("/usuario/", status_code=status.HTTP_200_OK)
async def atualizar_usuario(model: schemas.Usuario, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioUsuario(db).put(model)
    return retorno

@router.put("/usuario/senha-acesso/", status_code=status.HTTP_200_OK)
async def senha_acesso(model: schemas.SenhaAcessoUsuario, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    model.tx_senha = await hash_provider.gerar_hash(model.tx_senha)
    retorno = await RepositorioUsuario(db).senha_acesso(model)
    return retorno

@router.put("/usuario/esqueci-senha/", status_code=status.HTTP_200_OK)
async def esqueci_senha(model: schemas.SenhaAcessoUsuario, db: Session = Depends(get_db)):
    retorno = await RepositorioUsuario(db).get_by_id(model.nu_cpf)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {model.nu_cpf} informado!')
    model.tx_senha = await hash_provider.gerar_hash(model.tx_senha)
    retorno = await RepositorioUsuario(db).esqueci_senha(model)
    return retorno

@router.get("/usuario/{nu_cpf}", status_code=status.HTTP_200_OK, response_model=schemas.UsuarioLista)
async def pegar_usuario(nu_cpf: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioUsuario(db).get_by_id(nu_cpf, True)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')
    return retorno

@router.get("/usuario/redefinir-senha/{nu_cpf}/{url}", status_code=status.HTTP_200_OK)
async def redefinir_senha(nu_cpf: str, url:str, db: Session = Depends(get_db)):
    retorno = await RepositorioUsuario(db).get_by_id(nu_cpf, False)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o CPF: {nu_cpf} informado!')

    retorno = await RepositorioUsuario(db).redefinirSenha(retorno, url)
    return retorno
    return {'detail':'Link para criar nova senha enviado com sucesso'}

@router.delete("/usuario/{nu_cpf}", status_code=status.HTTP_200_OK)
async def apagar_usuario(nu_cpf: str, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioUsuario(db).delete(nu_cpf)
    return retorno