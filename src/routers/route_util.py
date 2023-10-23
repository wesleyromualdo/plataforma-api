from fastapi import APIRouter, HTTPException, status, Query
import socket
import platform
from src.utils import utils
from typing import List, Optional

router = APIRouter(tags=['Util'])

#@router.get('/dados')
#def listar_dados(usuario: schemas.Usuario = Depends(obter_usuario_logado), db: Session = Depends(get_db)):

@router.get("/ip_local", tags=['Util'], status_code=status.HTTP_200_OK)
async def pega_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    ip_address = s.getsockname()[0]

    return {'ip': ip_address, 'hostname': socket.gethostname(), 'os': platform.platform()}

@router.get("/envio-email", tags=['Util'], status_code=status.HTTP_200_OK)
async def carrega_tarefas_por_usuario(subject: Optional[str] = Query(default=None, max_length=200), 
                                        html_corpo: Optional[str] = Query(default=None, max_length=1000),
                                        email_user: Optional[str] = Query(default=None, max_length=100)):

    retorno = utils.envio_email(subject, html_corpo, email_user, [])
    return True
    if not retorno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não foi encontrado nenhum registro para o n° de CPF informado!')
    return retorno