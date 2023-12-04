from fastapi import FastAPI, Request, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from src.routers import (route_auth, route_dados_negocial, route_executor, route_logs, route_menu, 
    route_perfil, route_setor, route_tarefa, route_usuario, route_automacao, route_util, route_script,
    route_arquivos, route_controleexecucao, route_cofresenha)

from src.jobs.write_notification import write_notification
#from fastapi_socketio import SocketManager

'''from Controllers.MenuController import MenuController
from Controllers.SetorController import SetorController
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
        "name": "Setor",
        "description": "Este serviço tem o objetivo manter os registros de Setores"
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
        "name": "Executor",
        "description": "Este serviço tem o objetivo manter os registros de download dos executores",
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
    }
]

app = FastAPI(title="SOLVE AUTOMATION", openapi_tags=tags_metadata)
#socket_manager = SocketManager(app=app)
# CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
    "https://plataforma.automaxia.com.br",
    "https://plataforma.automaxia.com.br/",
    "http://plataforma.automaxia.com.br/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#pip install virtualenv
#python -m venv venv
#venv/Scripts/Activate
#uvicorn server:app --reload --reload-dir=src
#pip freeze > requirements.txt
#pip install -r requirements.txt
#upgrade-requirements

#pip instalar greenlet
#pip install backports.zoneinfo

#alembic init alembic
#alembic revision --autogenerate -m "Criando tabelas no banco de dados"
#alembic upgrade head

# Gerar chave secreta no gitbash
# openssl rand -hex 32

# AUTH
app.include_router(route_auth.router)

# USUÁRIO
app.include_router(route_usuario.router)

# SETOR
app.include_router(route_setor.router)

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

app.include_router(route_executor.router)

app.include_router(route_arquivos.router)

app.include_router(route_controleexecucao.router)

app.include_router(route_cofresenha.router)

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

'''@app.socket_manager.on('join')
async def handle_join(sid, *args, **kwargs):
    await socket_manager.emit('lobby', 'User joined')


@socket_manager.on('test')
async def test(sid, *args, **kwargs):
    await socket_manager.emit('hey', 'joe')

@socket_manager.on('sendMessage')
def send_message_handler(msg):
    socket_manager.emit('getMessage', msg)'''

'''
INSERT INTO public.setor(tx_sigla, tx_nome, bo_status)
VALUES('Solve', 'Área responsável pela execução e configuração inicial da ferramenta', true);

INSERT INTO public.perfil(tx_nome, tx_finalidade, bo_superuser, bo_status)
VALUES('Administrador', 'Responsável gerir os cadastros e configuração da ferramenta', true, true);

INSERT INTO public.perfil_usuario(nu_cpf, perfil_id)
VALUES('00000000191', (SELECT id FROM public.perfil WHERE tx_nome = 'Administrador'));

#senha = admin@solve

INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(1000, 'DashBoard', '/dashBoard', 'dashBoard', 1, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(2000, 'Tarefa', '/tarefa', 'assignment', 2, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(3000, 'Gestão de automação', '/automacao', 'settings', 3, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(4000, 'Gestão de usuário', '/usuario', 'group', 4, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(5000, 'Cadastro de Módulo', '/modulo', 'view_module', 5, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(6000, 'Cadastro de Perfil', '/perfil', 'assignment_ind', 6, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(7000, 'Cadastro de Setor', '/setor', 'supervised_user_circle', 7, true);

INSERT INTO public.perfil_menu(menu_id, perfil_id, setor_id)
(SELECT id, (SELECT id FROM public.perfil WHERE tx_nome = 'Solve'), (SELECT id FROM public.setor WHERE tx_sigla = 'Solve') FROM public.menu);
'''