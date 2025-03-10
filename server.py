from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.routers import (route_auth, route_dados_negocial, route_worker, route_logs, route_menu, 
    route_perfil, route_cliente, route_tarefa, route_usuario, route_automacao, route_util, route_script,
    route_arquivos, route_controleexecucao, route_cofresenha, route_configuracao, route_kafka)

from src.jobs.write_notification import write_notification
#from fastapi_socketio import SocketManager

from starlette.applications import Starlette
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

'''from Controllers.MenuController import MenuController
from Controllers.ClienteController import ClienteController
from Controllers.PerfilController import PerfilController
from Controllers.UsuarioController import UsuarioController
from Controllers.AutomacaoController import AutomacaoController'''

tags_metadata = [
    {
        "name": "Auth",
        "description": "Este serviço tem o objetivo gerar e validar o token de acesso"
    },
    {
        "name": "Usuário",
        "description": "Este serviço tem o objetivo manter os registros de Usuários"
    },
    {
        "name": "Cliente",
        "description": "Este serviço tem o objetivo manter os registros de Clientes"
    },
    {
        "name": "Menu",
        "description": "Este serviço tem o objetivo manter os registros de Menus",
    },
    {
        "name": "Perfil",
        "description": "Este serviço tem o objetivo manter os registros de Perfis",
    },
    {
        "name": "Automação",
        "description": "Este serviço tem o objetivo manter os registros de Automações",
    },
    {
        "name": "Tarefa",
        "description": "Este serviço tem o objetivo manter os registros de Tarefas",
    },
    {
        "name": "Logs",
        "description": "Este serviço tem o objetivo manter os registros de logs de execução da automação",
    },
    {
        "name": "DadosNegocial",
        "description": "Este serviço tem o objetivo manter os registros de Dados Negocial de execução da automação",
    },
    {
        "name": "Background Task",
        "description": "Você pode definir tarefas em segundo plano a serem executadas após retornar uma resposta",
    },
    {
        "name": "Script/Anexo",
        "description": "Este serviço tem o objetivo manter os registros de anexos de tarefas",
    },
    {
        "name": "Worker",
        "description": "Este serviço tem o objetivo manter os registros de download dos workers",
    },
    {
        "name": "Util",
        "description": "",
    },
    {
        "name": "Arquivos",
        "description": "Este serviço tem o objetivo mostrar os arquivos gerados pela execução",
    },
    {
        "name": "Controle Execução",
        "description": "Este serviço tem o objetivo controlar toda execução ja realizada pela automação",
    },
    {
        "name": "Cofre Senha",
        "description": "Este serviço tem o objetivo gerar um cofre de senha",
    },
    {
        "name": "Configuração",
        "description": "Este serviço tem o objetivo gerar variaveis de configuração para a aplicação",
    },
    {
        "name": "Kafka",
        "description": "Este serviço tem o objetivo consumer e producer de mensagens no Kafka",
    }
]

'''import requests
try:
    response = requests.get('http://apm-server.logging.svc.cluster.local:8200')
    response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
except requests.exceptions.RequestException as err:
    print(f"URL check failed: {err}")
else:
    print("URL check succeeded.")'''

app = FastAPI(title="PLATAFORMA AUTOMAXIA", openapi_tags=tags_metadata)
#socket_manager = SocketManager(app=app)
# CORS

'''apm = make_apm_client({
    'SERVICE_NAME': 'plataforma-api',
    'SECRET_TOKEN': 'P2JU0etR_1_-rhcmtojcXcCov8s',
    'SERVER_URL': 'http://apm-server.logging.svc.cluster.local:8200',
    'CAPTURE_HEADERS': True,
    'CAPTURE_BODY': 'all',
    'DEBUG': True,
    'LOG_LEVEL': 'DEBUG'
})
app.add_middleware(ElasticAPM, client=apm)'''

#apm_client = make_apm_client(apm_config)
#print(apm_client)
#app.add_middleware(ElasticAPM, client=apm_client)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
    "https://plataforma.automaxia.com.br",
    "http://plataforma.automaxia.com.br",
    "http://plataforma-web.automaxia.com.br",
    "http://plataforma-api.automaxia.com.br",
    "https://plataforma-web.automaxia.com.br",
    "https://plataforma-api.automaxia.com.br"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

#allow_methods=["GET", "POST", "PUT", "DELETE"],
#allow_headers=["Authorization", "Content-Type"],

#pip install virtualenv
#python -m venv venv
#venv/Scripts/Activate
#uvicorn server:app --reload --reload-dir=src
#pip freeze > requirements.txt
#pip install -r requirements.txt
#upgrade-requirements

#pip install greenlet
#pip install backports.zoneinfo

#alembic init alembic
#alembic revision --autogenerate -m "Alterando tabela de configuração"
#alembic upgrade head

# Gerar chave secreta no gitbash
# openssl rand -hex 32

# AUTH
app.include_router(route_auth.router)

# USUÁRIO
app.include_router(route_usuario.router)

# Cliente
app.include_router(route_cliente.router)

# MENU
app.include_router(route_menu.router)

# PERFIL
app.include_router(route_perfil.router)

# AUTOMAÇÃO
app.include_router(route_automacao.router)

# TAREFAS
app.include_router(route_tarefa.router)

# Util
app.include_router(route_util.router)

# Logs
app.include_router(route_logs.router)

# Dados Negocial
app.include_router(route_dados_negocial.router)

app.include_router(route_script.router)

app.include_router(route_worker.router)

app.include_router(route_arquivos.router)

app.include_router(route_controleexecucao.router)

app.include_router(route_cofresenha.router)

app.include_router(route_configuracao.router)

app.include_router(route_kafka.router)

'''@app.get("/external-service")
async def call_external_service():
    url = "http://external-service.example.com"
    headers = get_trace_parent_header()
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    return response.json()'''

@app.post("/send-notification/{email}", tags=['Background Task'])
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Teste de e-mail")
    return {"message": "Mensagem Enviada."}

@app.get("/health", response_class=PlainTextResponse)
def healthcheck():
    return "200"

# Middlewares
@app.middleware('http')
async def tempo_middleware(request: Request, next):
    #print('Interceptou chegou', request.method)
    response = await next(request)
    #print('Interceptou volta')
    return response
#socket_manager
#websocket.main()
