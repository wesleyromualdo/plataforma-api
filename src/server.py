from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from src.routers import route_auth, route_dados_negocial, route_logs, route_menu, route_perfil, route_setor, route_tarefa, route_usuario, route_automacao, route_util
from src.jobs.write_notification import write_notification

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
        "name": "Util",
        "description": "",
    }
]

app = FastAPI(title="SOLVE AUTOMATION", openapi_tags=tags_metadata)

# CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200",
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

@app.post("/send-notification/{email}", tags=['Background Task'])
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="Teste de e-mail")
    return {"message": "Mensagem Enviada."}

# Middlewares
@app.middleware('http')
async def tempo_middleware(request: Request, next):
    #print('Interceptou chegou', request.method)
    response = await next(request)
    #print('Interceptou volta')
    return response



'''
######################################################################################################################
#  SETOR                                                                                                             #
######################################################################################################################
@app.get("/setor", tags=['Setor'])
async def listar_todos_setores(setid: Union[int, None] = None,
                                setnome: Union[str, None] = Query(default=None, max_length=200),
                                setdsc: Union[str, None] = Query(default=None, max_length=500),
                                setstatus: Union[bool, None] = Query(default=True),
                                pagina: Union[int, None] = Query(default=0),
                                tamanho_pagina: Union[int, None] = Query(default=10)):

    setorControl = SetorController()
    retorno = await setorControl.get_all(setid, setnome, setdsc, setstatus, pagina, tamanho_pagina)
    return retorno

@app.get("/setor/{id_setor}", tags=['Setor'])
async def pegar_setor(id_setor: int):
    setorControl = SetorController()
    retorno = await setorControl.get_by_id(id_setor)
    return retorno

@app.post("/setor/", tags=['Setor'])
async def inserir_setor(setor: model.Setor):
    setorControl = SetorController()
    retorno = await setorControl.post(setor)
    return retorno

@app.put("/setor/", tags=['Setor'])
async def atualizar_setor(setor: model.Setor):
    setorControl = SetorController()
    retorno = await setorControl.put(setor)
    return retorno

@app.delete("/setor/{id_setor}", tags=['Setor'])
async def apagar_setor(id_setor: int):
    setorControl = SetorController()
    retorno = await setorControl.delete_by_id(id_setor)
    return retorno
######################################################################################################################
#  MENU                                                                                                              #
######################################################################################################################
@app.get("/menu", tags=['Menu'])
async def listar_todos_menus(mnuid: Union[int, None] = Query(default=None),
                                mnucod: Union[int, None] = Query(default=None),
                                mnucodpai: Union[int, None] = Query(default=None),
                                mnudsc: Union[str, None] = Query(default=None, max_length=100),
                                mnustatus: Union[bool, None] = Query(default=True),
                                pagina: Union[int, None] = Query(default=0),
                                tamanho_pagina: Union[int, None] = Query(default=10)):

    menuControl = MenuController()
    retorno = await menuControl.get_all(mnuid, mnucod, mnucodpai, mnudsc, mnustatus, pagina, tamanho_pagina)
    return retorno

@app.get("/menu/{id_menu}", tags=['Menu'])
async def pegar_menu(id_menu: int):
    menuControl = MenuController()
    retorno = await menuControl.get_by_id(id_menu)
    return retorno

@app.post("/menu/", tags=['Menu'])
async def inserir_menu(menu: model.Menu):
    menuControl = MenuController()
    retorno = await menuControl.post(menu)
    return retorno

@app.put("/menu/", tags=['Menu'])
async def atualizar_menu(menu: model.Menu):
    menuControl = MenuController()
    retorno = await menuControl.put(menu)
    return retorno

@app.delete("/menu/{id_menu}", tags=['Menu'])
async def apagar_menu(id_menu: int):
    menuControl = MenuController()
    retorno = await menuControl.delete_by_id(id_menu)
    return retorno
######################################################################################################################
#  PERFIL                                                                                                            #
######################################################################################################################
@app.get("/perfil", tags=['Perfil'])
async def listar_todos_perfis(pflid: Union[int, None] = Query(default=None),
                                pflnome: Union[str, None] = Query(default=None, max_length=200),
                                pflsuperuser: Union[bool, None] = Query(default=None),
                                pflsuporte: Union[bool, None] = Query(default=None),
                                pflstatus: Union[bool, None] = Query(default=True),
                                pagina: Union[int, None] = Query(default=0),
                                tamanho_pagina: Union[int, None] = Query(default=10)):

    perfilControl = PerfilController()
    retorno = await perfilControl.get_all(pflid, pflnome, pflsuperuser, pflsuporte, pflstatus, pagina, tamanho_pagina)
    return retorno

@app.get("/perfil/{id_perfil}", tags=['Perfil'])
async def pegar_menu(id_perfil: int):
    perfilControl = PerfilController()
    retorno = await perfilControl.get_by_id(id_perfil)
    return retorno

@app.post("/perfil/", tags=['Perfil'])
async def inserir_menu(menu: model.Menu):
    perfilControl = PerfilController()
    retorno = await perfilControl.post(menu)
    return retorno

@app.put("/perfil/", tags=['Perfil'])
async def atualizar_menu(menu: model.Menu):
    perfilControl = PerfilController()
    retorno = await perfilControl.put(menu)
    return retorno

@app.delete("/perfil/{id_perfil}", tags=['Perfil'])
async def apagar_menu(id_perfil: int):
    perfilControl = PerfilController()
    retorno = await perfilControl.delete_by_id(id_perfil)
    return retorno

@app.post("/perfil_setor/", tags=['Perfil'])
async def inserir_menu(menu: model.Menu):
    perfilControl = PerfilController()
    retorno = await perfilControl.post(menu)
    return retorno

######################################################################################################################
#  USUÁRIO                                                                                                           #
######################################################################################################################
@app.get("/usuario", tags=['Usuário'])
async def listar_todos_usuarios(usucpf: Union[int, None] = Query(default=None),
                                usunome: Union[str, None] = Query(default=None, max_length=200),
                                setid: Union[int, None] = Query(default=None),
                                usustatus: Union[bool, None] = Query(default=True),
                                pagina: Union[int, None] = Query(default=0),
                                tamanho_pagina: Union[int, None] = Query(default=10)):

    control = UsuarioController()
    retorno = await control.get_all(usucpf, usunome, setid, usustatus, pagina, tamanho_pagina)
    return retorno

@app.get("/usuario/{cpf}", tags=['Usuário'])
async def pegar_usuario(cpf: str):
    control = UsuarioController()
    retorno = await control.get_by_id(cpf)
    return retorno

@app.post("/usuario/", tags=['Usuário'])
async def inserir_usuario(modelo: model.Usuario):
    control = UsuarioController()
    retorno = await control.post(modelo, False)
    return retorno

@app.put("/usuario/", tags=['Usuário'])
async def atualizar_usuario(modelo: model.Usuario):
    control = UsuarioController()
    retorno = await control.put(modelo, False)
    return retorno

@app.delete("/usuario/{cpf}", tags=['Usuário'])
async def apagar_usuario(cpf: str):
    control = UsuarioController()
    retorno = await control.delete_by_id(cpf)
    return retorno

######################################################################################################################
#  AUTOMAÇÃO                                                                                                         #
######################################################################################################################
@app.get("/automacao", tags=['Automação'])
async def listar_todos_automacao(usucpf: Union[int, None] = Query(default=None),
                                usunome: Union[str, None] = Query(default=None, max_length=200),
                                setid: Union[int, None] = Query(default=None),
                                usustatus: Union[bool, None] = Query(default=True),
                                pagina: Union[int, None] = Query(default=0),
                                tamanho_pagina: Union[int, None] = Query(default=10)):

    control = AutomacaoController()
    retorno = await control.get_all(usucpf, usunome, setid, usustatus, pagina, tamanho_pagina)
    return retorno

@app.get("/automacao/{id_automacao}", tags=['Automação'])
async def pegar_automacao(id_automacao: str):
    control = AutomacaoController()
    retorno = await control.get_by_id(id_automacao)
    return retorno

@app.post("/automacao/", tags=['Automação'])
async def inserir_automacao(modelo: model.Automacao):
    control = AutomacaoController()
    retorno = await control.post(modelo, True)
    return retorno

@app.put("/automacao/", tags=['Automação'])
async def atualizar_automacao(modelo: model.Automacao):
    control = AutomacaoController()
    retorno = await control.put(modelo, False)
    return retorno

@app.delete("/automacao/{id_automacao}", tags=['Automação'])
async def apagar_automacao(id_automacao: str):
    control = AutomacaoController()
    retorno = await control.delete_by_id(id_automacao)
    return retorno
'''