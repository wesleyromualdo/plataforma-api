from fastapi import APIRouter, status, Depends, HTTPException
from src.routers.auth_utils import obter_usuario_logado

from fastapi.responses import FileResponse

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

@router.get("/arquivos/{diretorio}", tags=['Arquivos'], status_code=status.HTTP_200_OK)
async def pegar_arquivos_diretorio(diretorio: str, usuario = Depends(obter_usuario_logado)):
    import os, json

    file_path = os.getcwd() + f"/{diretorio}"    
    if os.path.isdir(file_path) is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado o diretório informado!')
    
    json_arquivo = []
    for dir, subpastas, arquivos in os.walk(file_path, topdown=True):
        
        for arquivo in arquivos:
            conteudo = os.path.join(dir, arquivo)
            ar_conteudo = conteudo.split(diretorio)
            arquivo = ar_conteudo[1]
            
            arquivo = diretorio+''+arquivo.replace('\\', '/')            

            file_size = os.path.getsize(conteudo)
            # List of units
            units = ["B", "KB", "MB", "GB", "TB"]
            # Iterate through the units and divide the size by 1024
            for unit in units:
                if file_size < 1024.0:
                    break
                file_size /= 1024.0
            size = f"{file_size:.2f} {unit}"
            json_arquivo.append({'arquivo': arquivo, 'tamanho':size})

    return json_arquivo

@router.get("/download/", tags=['Arquivos'], status_code=status.HTTP_200_OK)
async def download_arquivo_diretorio(diretorio: str, usuario = Depends(obter_usuario_logado)):
    import os

    if '/' in diretorio:
        ar_dir = diretorio.split('/')
    else:
        ar_dir = diretorio.split('\\')
    
    file_name = ar_dir[len(ar_dir)-1]

    file_path = os.getcwd() + f"/{diretorio}"
    if os.path.isfile(file_path):
        return FileResponse(path=file_path, media_type='application/octet-stream', filename=file_name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'O arquivo {file_name} não foi encontrado no diretório!')