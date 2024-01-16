import json
from pydantic import BaseModel, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from sqlalchemy.sql import func

class ClientePOST(BaseModel):
    tx_sigla: str
    tx_nome: str
    nu_worker: Optional[int] = None
    bo_status: Optional[bool] = True
    class Config:
        orm_mode = True

class UsuarioClienteAcesso(BaseModel):
    nu_cpf: str
    cliente_id: int
    dt_ultimoacesso: Optional[datetime] = None

class UsuarioCliente(BaseModel):
    id: int

class UsuarioSimples(BaseModel):
    nu_cpf: str
    tx_nome: str
    tx_email: EmailStr
    bo_status: Optional[bool] = True
    class Config:
        orm_mode = True

class Cliente(ClientePOST):
    id: Optional[int] = None    
    class Config:
        orm_mode = True

class ClienteLista(Cliente):
    usuarios: List[UsuarioSimples] = None    
    class Config:
        orm_mode = True

class UsuarioPOST(BaseModel):
    nu_cpf: str
    tx_nome: str
    tx_email: EmailStr
    tx_foto: Optional[str] = None
    bo_status: Optional[bool] = True
    cliente: List[UsuarioCliente] = None

class Usuario(BaseModel):
    nu_cpf: str
    tx_nome: str
    tx_senha: Optional[str] = ''
    tx_email: EmailStr
    tx_foto: Optional[str] = None
    dt_inclusao: Optional[datetime] = None
    bo_status: Optional[bool] = True
    cliente: List[UsuarioCliente] = None

    class Config:
        orm_mode = True

class SenhaAcessoUsuario(BaseModel):
    nu_cpf: str
    tx_senha: str
    tx_senha_confirma: str

class PerfilMenu(BaseModel):
    id: str
    cliente_id: int

class PerfilPOST(BaseModel):
    tx_nome: str
    tx_finalidade: Optional[str] = ''
    constante_virtual: Optional[str] = ''
    bo_superuser: Optional[bool] = False
    bo_status: Optional[bool] = True
    bo_delegar: Optional[bool] = False
    menu: List[PerfilMenu] = None
    class Config:
        orm_mode = True

class Perfil(PerfilPOST):
    id: Optional[int] = None
    class Config:
        orm_mode = True

class LoginData(BaseModel):
    nu_cpf: str
    tx_senha: str
    class Config:
        orm_mode = True

class LoginSucesso(BaseModel):
    usuario: UsuarioSimples
    access_token: str
    token_type: Optional[str] = 'bearer'
    class Config:
        orm_mode = True

class MenuPOST(BaseModel):
    nu_codigo: int
    tx_nome: str
    tx_link: str
    tx_icon: str
    nu_ordem: int
    bo_status: Optional[bool] = True
    class Config:
        orm_mode = True

class Menu(MenuPOST):
    id: Optional[int] = None
    class Config:
        orm_mode = True

class MenuLista(Menu):
    perfil: List[Perfil] = None
    class Config:
        orm_mode = True

class PerfilLista(Perfil):
    menu: List[Menu] = None
    #usuario: List[Usuario]
    class Config:
        orm_mode = True

class AutomacaoPOST(BaseModel):
    cliente_id: int
    tx_nome: Optional[str] = ''
    nu_cpf: Optional[str] = ''
    tx_descricao: Optional[str] = ''
    tx_constante_virtual: Optional[str] = ''
    bo_status: Optional[bool] = True
    tx_json: Optional[str] = ''
    nu_qtd_tarefa: Optional[int] = None
    nu_qtd_download: Optional[int] = None
    class Config:
        orm_mode = True

class DownloadWorkerPOST(BaseModel):
    cliente_id: int
    automacao_id: int
    tx_nome: str
    nu_cpf: Optional[str] = ''
    tx_hostname: Optional[str] = ''
    tx_json: Optional[str] = ''
    tx_ip: Optional[str] = ''
    tx_ip_mac: Optional[str] = ''
    tx_os: Optional[str] = ''
    tx_processador: Optional[str] = ''
    nu_cpu: Optional[int] = None
    tx_memoria: Optional[str] = ''
    tx_hd: Optional[str] = ''
    tx_hd_livre: Optional[str] = ''
    tx_diretorio: Optional[str] = ''

class DownloadWorker(DownloadWorkerPOST):
    id: Optional[int] = None
    dt_download: Optional[datetime] = None
    dt_alive: Optional[datetime] = None
    bo_status: Optional[bool] = True
    bo_ativo: Optional[bool] = True
    class Config:
        orm_mode = True

class Automacao(AutomacaoPOST):
    id: Optional[int] = None
    class Config:
        orm_mode = True

class PerfilID(BaseModel):
    id: int
    class Config:
        orm_mode = True

class AutomacaoID(BaseModel):
    id: int
    class Config:
        orm_mode = True

class DadosAcessoUsuario(BaseModel):
    perfil: List[PerfilID]
    automacao: List[AutomacaoID]
    cliente_id:int
    nu_cpf: str

class UsuarioLista(BaseModel):
    nu_cpf: str
    tx_nome: str
    tx_email: EmailStr
    dt_inclusao: datetime
    bo_status: Optional[bool] = True
    tx_foto: Optional[str] = None
    cliente: List[Cliente] = None
    perfil: List = None
    automacao: List = None
    class Config:
        orm_mode = True

class PerfilUsuario(BaseModel):
    nu_cpf: str
    perfil_id: int

    class Config:
        orm_mode = True

class AutomacaoUsuario(BaseModel):
    nu_cpf: str
    automacao_id: Optional[int] = None
    cliente_id: Optional[int] = None

    class Config:
        orm_mode = True

class PerfilMenu(BaseModel):
    menu_id: int
    perfil_id: int
    cliente_id: int

    class Config:
        orm_mode = True

'''class PerfilAutomacao(BaseModel):
    perfil_id: int
    automacao_id: int

    class Config:
        orm_mode = True'''
class IniciaTarefa(BaseModel):
    tarefa_id: int
    cliente_id: int
    automacao_id: Optional[int] = None
    nu_cpf: str
    tx_json: Optional[str] = None

class TarefaPOST(BaseModel):
    automacao_id: Optional[int] = None
    nu_cpf: Optional[str] = ''
    cliente_id: Optional[int] = None
    tx_nome: Optional[str] = ''
    bo_agendada: Optional[bool] = False
    bo_execucao: Optional[bool] = False
    bo_email: Optional[bool] = False
    bo_status: Optional[bool] = True
    json_agendamento: Optional[str] = ''
    tx_assunto_inicia: Optional[str] = ''
    tx_corpo_email_inicia: Optional[str] = ''
    tx_assunto_finaliza: Optional[str] = ''
    tx_corpo_email_finaliza: Optional[str] = ''
    tx_nome_script: Optional[str] = ''
    nu_prioridade: Optional[int] = None
    historico_id: Optional[int] = None
    tx_json: Optional[str] = ''
    tx_constante_virtual: Optional[str] = ''
    class Config:
        orm_mode = True

class Tarefa(TarefaPOST):
    id: Optional[int] = ''
    tx_situacao: Optional[str] = ''
    dt_inclusao: Optional[datetime] = None
    dt_alteracao: Optional[datetime] = None
    anexo_script_id: Optional[str] = None
    bo_alterou_automacao: Optional[bool] = None
    class Config:
        orm_mode = True

class TarefaLista(Tarefa):
    automacao: Optional[Automacao] = None
    class Config:
        orm_mode = True

class AutomacaoLista(Automacao):
    dt_inclusao: Optional[datetime] = None
    cliente: Optional[Cliente] = None
    tarefa: List[Tarefa]
    download: List[DownloadWorker]
    class Config:
        orm_mode = True

class StopTarefa(BaseModel):
    tarefa_id: int
    dt_fim: Optional[str] = ''
    bo_status_code: Optional[str] = ''
    tx_resumo: Optional[str] = ''

class TarefaHistoricoPOST(BaseModel):
    tarefa_id: int
    automacao_id: Optional[int] = None
    nu_cpf: str
    dt_inicio: Optional[datetime] = None
    dt_fim: Optional[datetime] = None
    bo_status_code: Optional[int] = None
    tx_resumo: Optional[str] = ''
    tx_ip_execucao: Optional[str] = ''
    tx_json: Optional[str] = ''
    class Config:
        orm_mode = True

class TarefaHistorico(TarefaHistoricoPOST):
    id: Optional[int] = None
    class Config:
        orm_mode = True

class TarefaHistoricoLista(TarefaHistorico):
    id: Optional[int] = None
    #tarefa: Optional[Tarefa] = None
    automacao: List[Automacao] = None
    class Config:
        orm_mode = True

class PerfilTarefa(BaseModel):
    tarefa_id: int
    perfil_id: int
    class Config:
        orm_mode = True

class LogsPOST(BaseModel):
    historico_tarefa_id: int
    tx_status: Optional[str] = ''
    tx_acao_auxiliar: Optional[str] = ''
    tx_descricao: Optional[str] = ''
    tx_json: Optional[str] = ''
    class Config:
        orm_mode = True

class Logs(LogsPOST):
    id: Optional[int] = None
    class Config:
        orm_mode = True

class LogsLista(Logs):
    id: Optional[int] = None
    dt_inclusao: Optional[datetime] = None
    class Config:
        orm_mode = True

class DadoNegocialPOST(BaseModel):
    historico_tarefa_id: int
    tx_descricao: Optional[str] = ''
    dt_inicio: Optional[datetime] = None
    dt_fim: Optional[datetime] = None
    tx_status: Optional[str] = ''
    tx_json: Optional[str] = ''
    class Config:
        orm_mode = True

class DadoNegocial(DadoNegocialPOST):
    id: int
    class Config:
        orm_mode = True

class DadoNegocialLista(DadoNegocial):
    id: int
    class Config:
        orm_mode = True

class ControleExecucaoPOST(BaseModel):
    tarefa_id: int
    tx_descricao: Optional[str] = ''
    tx_json: Optional[str] = ''
    class Config:
        orm_mode = True

class ControleExecucao(ControleExecucaoPOST):
    id: int
    bo_status: Optional[bool] = None
    class Config:
        orm_mode = True

class ControleExecucaoLista(ControleExecucao):
    id: int
    bo_status: Optional[bool] = None
    dt_cadastro: Optional[datetime] = None
    class Config:
        orm_mode = True

class AnexoScriptPOST(BaseModel):
    tarefa_id: int
    tx_nome: Optional[str] = ''
    tx_extensao: Optional[str] = ''
    tx_tipo: Optional[str] = ''
    nu_tamanho: Optional[float] = None
    nu_arquivo: Optional[int] = None
    nu_versao: Optional[int] = None
    nu_cpf: Optional[str] = ''
    class Config:
        orm_mode = True

class AnexoScript(AnexoScriptPOST):
    id: int
    class Config:
        orm_mode = True

class AnexoScriptLista(AnexoScript):
    dt_inclusao: Optional[datetime] = None
    dt_download: Optional[datetime] = None
    bo_status: Optional[bool] = True
    class Config:
        orm_mode = True

class CofreSenhaPOST(BaseModel):
    cliente_id: int
    tx_nome: Optional[str] = ''
    tx_usuario: Optional[str] = ''
    tx_senha: Optional[str] = ''
    class Config:
        orm_mode = True

class CofreSenha(CofreSenhaPOST):
    id: int
    class Config:
        orm_mode = True

class CofreSenhaLista(CofreSenha):
    dt_inclusao: Optional[datetime] = None
    bo_status: Optional[bool] = True
    class Config:
        orm_mode = True

class Message(BaseModel):
    message: str
