from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.anexo_script import RepositorioAnexoScript

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

@router.get("/script", tags=['Script/Anexo'], status_code=status.HTTP_200_OK, response_model=List[schemas.AnexoScriptLista])
async def listar_todos_scripts(tarefa_id: Optional[int] = Query(default=None), 
                            tx_nome: Optional[str] = Query(default=None),
                            nu_cpf: Optional[str] = Query(default=None),
                            pagina: Optional[int] = Query(default=0),
                            tamanho_pagina: Optional[int] = Query(default=0), 
                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioAnexoScript(db).get_all(tarefa_id, tx_nome, nu_cpf, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.post("/script/", tags=['Script/Anexo'], status_code=status.HTTP_201_CREATED, response_model=schemas.AnexoScriptLista)
async def upload_script(model: schemas.AnexoScriptPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAnexoScript(db).post(model)
    return retorno

@router.put("/script/dt_download", tags=['Script/Anexo'], status_code=status.HTTP_200_OK, response_model=schemas.AnexoScriptLista)
async def atualizar_script_dt_download(script_id: int, dt_download: Optional[str] = Query(default=None), db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAnexoScript(db).put(script_id, dt_download)
    return retorno

@router.get("/script/tarefa/{tarefa_id}", tags=['Script/Anexo'], status_code=status.HTTP_200_OK, response_model=schemas.AnexoScriptLista)
async def pegar_script_tarefa(tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAnexoScript(db).get_by_tarefa_id(tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id da tarefa: {tarefa_id} informado!')
    return retorno

@router.delete("/script/{script_id}", tags=['Script/Anexo'], status_code=status.HTTP_200_OK)
async def apagar_script(script_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioAnexoScript(db).delete(script_id)
    return retorno
