from fastapi import status, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from src.providers import token_provider
from src.schemas.schemas import Usuario
from src.sqlalchemy.repositorios.usuario import RepositorioUsuario
from src.sqlalchemy.config.database import get_db

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/login')

async def obter_usuario_logado(token: str = Depends(oauth2_schema), db: Session=Depends(get_db)) -> Usuario:

    try:
        nr_cpf: str = await token_provider.verificar_access_token(token)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token inválido', headers={"WWW-Authenticate": "Bearer"})

    if nr_cpf == 'expirou':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expirou', headers={"WWW-Authenticate": "Bearer"})

    if not nr_cpf:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token inválido, CPF não encontrado', headers={"WWW-Authenticate": "Bearer"})
        
    usuario = await RepositorioUsuario(db).get_by_id(nr_cpf)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token inválido, Usuário não encontrado', headers={"WWW-Authenticate": "Bearer"})

    return usuario