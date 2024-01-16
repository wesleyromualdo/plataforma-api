import json
from unicodedata import name
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Float
from src.sqlalchemy.config.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Cliente(Base):
    __tablename__ = 'cliente'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tx_sigla = Column(String(20))
    tx_nome = Column(String(200))
    nu_worker = Column(Integer, server_default='1', default=1)
    bo_status = Column(Boolean, server_default='t', default=True)
    usuarios = relationship('Usuario', secondary='usuario_cliente', viewonly=True)
    #usuarios = relationship('Usuario', back_populates='cliente')

class Usuario(Base):
    __tablename__ = 'usuario'
    
    nu_cpf = Column(String(11), primary_key=True, index=True)
    tx_nome = Column(String(300))
    tx_senha = Column(String(300))
    tx_email = Column(String(300))
    tx_foto = Column(Text)
    bo_status = Column(Boolean, server_default='t', default=True)
    bo_worker = Column(Boolean, server_default='f', default=False)
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    cliente = relationship('Cliente', secondary="usuario_cliente", viewonly=True)
    #perfil = relationship('Perfil', secondary="perfil_usuario", viewonly=True)
    #cliente = relationship('Cliente', back_populates='usuarios')

class UsuarioCliente(Base):
    __tablename__ = 'usuario_cliente'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_usuariocliente_usuario'))
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_usuariocliente_cliente'))
    dt_ultimoacesso = Column(DateTime(timezone=False))

class Menu(Base):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nu_codigo = Column(Integer)
    tx_nome = Column(String(100))
    tx_link = Column(String(100))
    tx_icon = Column(String(100))
    nu_ordem = Column(Integer, server_default='1', default='1')
    bo_status = Column(Boolean, server_default='t', default=True)
    #perfil = relationship('Perfil', secondary="perfil_menu", viewonly=True)
    #perfil = relationship('PerfilMenu', back_populates='perfil')
    #perfil = relationship('PerfilMenu', backref='menu')

class Perfil(Base):
    __tablename__ = 'perfil'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tx_nome = Column(String(200))
    tx_finalidade = Column(String(1000))
    bo_superuser = Column(Boolean, server_default='f', default=False)
    bo_status = Column(Boolean, server_default='t', default=True)
    bo_delegar = Column(Boolean, server_default='f', default=False)
    constante_virtual = Column(String(100))
    menu = relationship('Menu', secondary="perfil_menu", viewonly=True)
    #usuario = relationship('Usuario', secondary='perfil_usuario', viewonly=True)
    #cliente = relationship('Menu', secondary="perfil_menu", viewonly=True)
    #perfilmenu = relationship('Perfil', backref='perfil')

class PerfilMenu(Base):
    __tablename__ = 'perfil_menu'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey('menu.id', name='fk_perfilmenu_menu'))
    perfil_id = Column(Integer, ForeignKey('perfil.id', name='fk_perfilmenu_perfil'))
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_perfilmenu_cliente'))

    #perfis = relationship('Perfil', back_populates='perfilmenu')
    #menus = relationship('Menu', back_populates='perfis')

class Automacao(Base):
    __tablename__ = 'automacao'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_automacao_cliente'))
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_automacao_usuario'))
    tx_nome = Column(String(200))
    tx_descricao = Column(String(200))
    tx_constante_virtual = Column(String(100))
    nu_qtd_tarefa = Column(Integer, server_default='1', default='1')
    nu_qtd_download = Column(Integer, server_default='1', default='1')
    bo_status = Column(Boolean, server_default='t', default=True)
    tx_json = Column(Text)
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    cliente = relationship('Cliente', backref='cliente')
    #cliente = relationship('cliente', secondary='cliente', viewonly=True)
    tarefa = relationship('Tarefa', back_populates='automacao')
    download = relationship('DownloadWorker', back_populates='automacao')

class DownloadWorker(Base):
    __tablename__ = 'download_worker'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_download_worker_cliente'))
    automacao_id = Column(Integer, ForeignKey('automacao.id', name='fk_download_worker_automacao'))
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_download_worker_usuario'))
    tx_nome = Column(String(200))
    tx_ip_mac = Column(String(30))    
    tx_ip = Column(String(30))
    tx_hostname = Column(String(200))
    tx_os = Column(String(200))
    tx_processador = Column(String(200))
    nu_cpu = Column(Integer)
    tx_memoria = Column(String(10))
    tx_hd = Column(String(10))
    tx_hd_livre = Column(String(10))
    tx_diretorio = Column(String(500))
    dt_download = Column(DateTime(timezone=False), server_default=func.now())
    dt_alive = Column(DateTime(timezone=False), server_default=func.now())
    tx_json = Column(Text)
    bo_status = Column(Boolean, server_default='t', default=True)
    bo_ativo = Column(Boolean, server_default='t', default=True)
    automacao = relationship('Automacao', back_populates='download')

class AutomacaoUsuario(Base):
    __tablename__ = 'automacao_usuario'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_automacao_usuario_usuario'))
    automacao_id = Column(Integer, ForeignKey('automacao.id', name='fk_automacao_usuario_automacao'))
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_automacao_usuario_cliente'))


class PerfilUsuario(Base):
    __tablename__ = 'perfil_usuario'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_perfilusuario_usuario'))
    perfil_id = Column(Integer, ForeignKey('perfil.id', name='fk_perfilusuario_perfil'))
    #usuario = relationship('Usuario', backref='perfil')

class Tarefa(Base):
    __tablename__ = 'tarefa'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    automacao_id = Column(Integer, ForeignKey('automacao.id', name='fk_tarefa_automacao'))
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_tarefa_cliente'))
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_tarefa_usuario'))
    historico_id = Column(Integer)
    tx_nome = Column(String(200))
    tx_situacao = Column(String(200))
    bo_agendada = Column(Boolean, server_default='f', default=False)
    bo_execucao = Column(Boolean, server_default='f', default=False)
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    dt_alteracao = Column(DateTime(timezone=False), server_default=func.now())
    bo_status = Column(Boolean, server_default='t', default=True)
    bo_email = Column(Boolean, server_default='f', default=False)
    json_agendamento = Column(Text)
    tx_assunto_inicia = Column(String(200))
    tx_corpo_email_inicia = Column(Text)
    tx_assunto_finaliza = Column(String(200))
    tx_corpo_email_finaliza = Column(Text)
    tx_nome_script = Column(String(300))
    nu_prioridade = Column(Integer, server_default='1', default='1')
    tx_json = Column(Text)
    tx_constante_virtual = Column(String(100))
    anexo_script_id = Column(Integer)
    #automacao = relationship('Automacao', secondary='automacao', viewonly=True)
    #automacao = relationship('Automacao')
    automacao = relationship('Automacao', back_populates='tarefa')
        
class AnexoScript(Base):
    __tablename__ = 'anexo_script'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id', name='fk_tarefa_anexo_script'))
    nu_cpf = Column(String(11))
    tx_nome = Column(String(200))
    tx_extensao = Column(String(50))
    tx_tipo = Column(String(50))
    nu_tamanho = Column(Float)
    nu_arquivo = Column(Integer)
    nu_versao = Column(Integer)
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    dt_download = Column(DateTime(timezone=False))
    bo_status = Column(Boolean, server_default='t', default=True)

class TarefaHistorico(Base):
    __tablename__ = 'tarefa_historico'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id', name='fk_tarefahistorico_tarefa'))
    automacao_id = Column(Integer, ForeignKey('automacao.id', name='fk_tarefahistorico_automacao'))
    nu_cpf = Column(String(11), ForeignKey('usuario.nu_cpf', name='fk_tarefahistorico_usuario'))
    dt_inicio = Column(DateTime(timezone=False), server_default=func.now())
    dt_fim = Column(DateTime(timezone=False))
    bo_status_code = Column(Integer)
    tx_ip_execucao = Column(String(20))
    tx_resumo = Column(Text)
    tx_json = Column(Text)

class PerfilTarefa(Base):
    __tablename__ = 'perfil_tarefa'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id', name='fk_perfiltarefa_tarefa'))
    perfil_id = Column(Integer, ForeignKey('perfil.id', name='fk_perfiltarefa_perfil'))

class Logs(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    historico_tarefa_id = Column(Integer, ForeignKey('tarefa_historico.id', name='fk_logs_historicotarefa'))
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    tx_status = Column(String(50))
    tx_acao_auxiliar = Column(Text)
    tx_descricao = Column(Text)
    tx_json = Column(Text)

class DadoNegocial(Base):
    __tablename__ = 'dado_negocial'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    historico_tarefa_id = Column(Integer, ForeignKey('tarefa_historico.id', name='fk_dadosnegocial_historicotarefa'))
    tx_descricao = Column(String(300))
    dt_inicio = Column(DateTime(timezone=False), server_default=func.now())
    dt_fim  = Column(DateTime(timezone=False))
    tx_status = Column(String(50))
    tx_json = Column(Text)

class ControleExecucao(Base):
    __tablename__ = 'controle_execucao'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tarefa_id = Column(Integer, ForeignKey('tarefa.id', name='fk_controle_execucao_tarefa'))
    tx_descricao = Column(String(300))
    dt_cadastro = Column(DateTime(timezone=False), server_default=func.now())
    bo_status = Column(Boolean, server_default='t', default=True)
    tx_json = Column(Text)

class CofreSenha(Base):
    __tablename__ = 'cofre_senha'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('cliente.id', name='fk_cofre_senha_cliente'))
    tx_nome = Column(String(300))
    tx_usuario = Column(String(50))
    tx_senha = Column(String(300))
    bo_status = Column(Boolean, server_default='t', default=True)
    dt_inclusao = Column(DateTime(timezone=False), server_default=func.now())
    