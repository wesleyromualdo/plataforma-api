from datetime import datetime, timedelta, timezone
from jose import jwt
import pytz, traceback
from src.utils import utils

#CONFIG  automaxia-automation-bot

SECRET_KEY = '6a0801ecf06dcef8ee930375a12593a39077e855'
ALGORITHM = 'HS256'
EXPIRES_IN_MIN = 480

AMSP = pytz.timezone('America/Sao_Paulo')

async def gerar_access_token(data: dict, expira_min: int = EXPIRES_IN_MIN) -> str:
    dados = data.copy()
    utc_dt = datetime.now(timezone.utc)
    dataAtual = utc_dt.astimezone(AMSP)

    #dataUTC = datetime.utcnow()

    if expira_min == '':
        expira_min = EXPIRES_IN_MIN

    expira = dataAtual + timedelta(minutes=expira_min)
    expira = str(expira).replace('-03:00', '')

    dados.update({'expira': expira})
    token_jwt = jwt.encode(dados, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

async def verificar_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        utc_dt = datetime.now(timezone.utc)
        dataAtual = utc_dt.astimezone(AMSP)
        dataAtual = str(dataAtual).replace('-03:00', '').split('.')[0]
        
        expira = payload['expira'].split('.')[0]
        expira = datetime.strptime(expira, '%Y-%m-%d %H:%M:%S')
        dataAtual = datetime.strptime(dataAtual, '%Y-%m-%d %H:%M:%S')

        segundoDif = (expira - dataAtual).total_seconds()
        if segundoDif < 0:
            return 'expirou'

        return payload.get('sub')
    except Exception as error:
        utc_dt = datetime.now(timezone.utc)
        dataErro = utc_dt.astimezone(AMSP)
        utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
        return {'detail': f'Erro na execução: '+str(error)}