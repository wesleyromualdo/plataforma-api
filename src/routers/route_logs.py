from fastapi import APIRouter, status, Depends, HTTPException, Query, UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session
from src.routers.auth_utils import obter_usuario_logado

from src.sqlalchemy.config.database import get_db
from src.schemas import schemas
from src.sqlalchemy.repositorios.log import RepositorioLogs

from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
from fastapi.routing import APIRoute
from fastapi.responses import FileResponse
import os, uuid, traceback

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

@router.get("/logs", tags=['Logs'], status_code=status.HTTP_200_OK)
async def listar_todos_logs(historico_id: Optional[int] = Query(default=None),
                            tx_descricao: Optional[str] = Query(default=None),
                            pagina: Optional[str] = Query(default=''),
                            tamanho_pagina: Optional[int] = Query(default=None), 
                            db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):

    retorno = await RepositorioLogs(db).get_all(historico_id, tx_descricao, pagina, tamanho_pagina)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o(s) filtro(s) informado(s)!')
    return retorno

@router.get("/logs/historico-tarefa-mensal", tags=['Logs'], status_code=status.HTTP_200_OK)
async def pegar_relatorio_mensal_historico_tarefa(cliente_id: Optional[str] = Query(default=None),
                                                  tarefa_id: Optional[str] = Query(default=None),
                                                  dt_inicio: Optional[str] = Query(default=None),
                                                  dt_fim: Optional[str] = Query(default=None), 
                                                  db: Session = Depends(get_db)):
    retorno = await RepositorioLogs(db).pegar_relatorio_mensal_historico_tarefa(cliente_id, tarefa_id, dt_inicio,dt_fim)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro de historico para os filtros informado!')
    return retorno

@router.post("/logs/", tags=['Logs'], status_code=status.HTTP_201_CREATED, response_model=schemas.LogsLista)
async def inserir_log(model: schemas.LogsPOST, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    if model.historico_tarefa_id == '' or model.historico_tarefa_id == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O id do histórico da tarefa não encontrado!')
    retorno = await RepositorioLogs(db).post(model)
    return retorno

@router.put("/logs/", tags=['Logs'], status_code=status.HTTP_200_OK, response_model=schemas.LogsLista)
async def atualizar_log(model: schemas.Logs, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).put(model)
    return retorno

@router.get("/logs/historico-tarefa/{historico_tarefa_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def pegar_logs_por_historico_tarefa_id(historico_tarefa_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    if historico_tarefa_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O ID da tarefa histórica não pode ser None.")
    
    retorno = await RepositorioLogs(db).get_logs_por_historico_id(historico_tarefa_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para a tarefa de id: {historico_tarefa_id} informado!')
    return retorno

@router.get("/logs/{log_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def pegar_log(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).get_by_id(log_id)
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o id: {log_id} informado!')
    return retorno

@router.delete("/logs/{log_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def apagar_log(log_id: int, db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).delete(log_id)
    return retorno

@router.post("/logs/elasticsearch", tags=['Logs'], status_code=status.HTTP_201_CREATED)
async def inserir_doc_elastic(model: schemas.LogsElastic, db: Session = Depends(get_db)):
    retorno = await RepositorioLogs(db).inserir_doc_elastic(model)
    return retorno

@router.get("/logs/download-image/{log_id}", tags=['Logs'], status_code=status.HTTP_200_OK)
async def download_imagem(log_id: int,db: Session = Depends(get_db), usuario = Depends(obter_usuario_logado)):
    retorno = await RepositorioLogs(db).get_by_id(log_id)

    file_path = retorno.tx_imagem
    file_name = os.path.basename(file_path)
    
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O arquivo {file_name} não foi encontrado no diretório!')
    
@router.post("/logs/upload-image/", tags=['Logs'], status_code=status.HTTP_200_OK)
async def upload_image(file: UploadFile, db: Session = Depends(get_db)):
    try:
        contents = file.file.read()
        nome_arquivo = f"{uuid.uuid4()}.png"
        diretorio = f"/data/plataforma/image"
        os.makedirs(diretorio, exist_ok=True)
        caminho_arquivo = f"{diretorio}/{nome_arquivo}"
        print(caminho_arquivo)

        with open(caminho_arquivo, 'wb') as f:
            f.write(contents)

        return {"detail": f"Successfully uploaded {file.filename}", "arquivo":f"{caminho_arquivo}"}
        
    except Exception as error:
        print(traceback.format_exc())
        return {'detail': f'Erro na execução: '+str(error)}