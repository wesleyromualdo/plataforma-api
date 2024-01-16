from sqlalchemy import select, delete, update, join
from sqlalchemy.orm import Session
from src.sqlalchemy.models import models
from src.schemas import schemas
from src.utils import utils
import traceback
from datetime import datetime, date, timezone
import pytz
AMSP = pytz.timezone('America/Sao_Paulo')

class RepositorioUsuario():
    
    def __init__(self, db: Session):
        self.db = db

    async def get_by_id(self, nu_cpf: str, relation = False) -> models.Usuario:
        try:
            stmt = select(models.Usuario).where(models.Usuario.nu_cpf == nu_cpf)
            db_orm = self.db.execute(stmt).scalars().first()

            if relation:
                perfil = await self.get_usuario_by_perfil(nu_cpf)
                db_orm.perfil = perfil

                automacao = await self.get_usuario_by_automacao(nu_cpf)
                db_orm.automacao = automacao

            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_usuario_by_perfil(self, nu_cpf: str):
        try:
            j = join(models.Perfil, models.PerfilUsuario, models.Perfil.id == models.PerfilUsuario.perfil_id)
            stmt = select(models.Perfil).select_from(j).where(models.PerfilUsuario.nu_cpf == nu_cpf)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_usuario_by_cliente(self, nu_cpf: str):
        try:
            j = join(models.Cliente, models.UsuarioCliente, models.Cliente.id == models.UsuarioCliente.cliente_id)
            stmt = select(models.Cliente).select_from(j).where(models.UsuarioCliente.nu_cpf == nu_cpf)
            db_orm = self.db.execute(stmt).scalars().all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_usuario_by_automacao(self, nu_cpf: str):
        try:
            j = join(models.Automacao, models.AutomacaoUsuario, models.Automacao.id == models.AutomacaoUsuario.automacao_id)
            stmt = select([models.Automacao.id, models.Automacao.nu_cpf,
                models.Automacao.cliente_id,
                models.Automacao.tx_nome,
                models.Automacao.tx_descricao,
                models.Automacao.nu_qtd_tarefa,
                models.Automacao.nu_qtd_download]
            ).select_from(j).where(models.AutomacaoUsuario.nu_cpf == nu_cpf)
            db_orm = self.db.execute(stmt).all()
            return db_orm
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def get_all(self, nu_cpf, tx_nome, cliente_id, bo_status, pagina, tamanho_pagina):
        try:
            '''j = join(models.Usuario, models.UsuarioCliente, models.Usuario.nu_cpf == models.UsuarioCliente.nu_cpf)
            result = self.db.query(models.Usuario).select_from(j)

            if nu_cpf:
                result = result.filter(models.Usuario.nu_cpf == nu_cpf)

            if tx_nome:
                result = result.filter(models.Usuario.tx_nome == tx_nome)

            if cliente_id:
                result = result.filter(models.UsuarioCliente.cliente_id == cliente_id)

            if str(bo_status) and bo_status is not None:
                result = result.filter(models.Usuario.bo_status == bo_status)

            result = result.filter(models.Usuario.bo_worker == False)

            if tamanho_pagina > 0:
                result.offset(pagina).limit(tamanho_pagina)
            
            return result.all()'''
            filtro = ''

            if nu_cpf:
                filtro += f" and u.nu_cpf = '{nu_cpf}'"

            if str(bo_status) and bo_status is not None:
                filtro += f" and u.bo_status = {bo_status}"

            if cliente_id:
                filtro += f" and us.cliente_id = {cliente_id}"

            if tx_nome:
                filtro += f" and u.tx_nome ilike '%{tx_nome}%'"

            sql = f"""SELECT u.nu_cpf, u.tx_nome, u.tx_email, u.bo_status, u.dt_inclusao, u.bo_worker,
                        array_agg(DISTINCT p.bo_superuser) AS perfil, array_agg(DISTINCT s.tx_sigla) AS cliente
                    FROM usuario u 
                        INNER JOIN usuario_cliente us ON us.nu_cpf = u.nu_cpf
                        INNER JOIN perfil_usuario pu ON pu.nu_cpf = u.nu_cpf
                        INNER JOIN perfil p ON p.id = pu.perfil_id
                        INNER JOIN cliente s ON s.id = us.cliente_id AND s.bo_status = TRUE
                    WHERE u.bo_worker = FALSE
                        {filtro} 
                    GROUP BY u.nu_cpf, u.tx_nome, u.tx_email, u.bo_status, u.dt_inclusao, u.bo_worker
                    ORDER BY u.tx_nome"""
            result = self.db.execute(sql).all()
            return result
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def dados_acesso(self, ormP: schemas.DadosAcessoUsuario):
        try:
            await self.deletePerfil(ormP.nu_cpf)
            for perfil in ormP.perfil:
                db_orm = models.PerfilUsuario(
                    nu_cpf = ormP.nu_cpf,
                    perfil_id = perfil.id
                )
                self.db.add(db_orm)

            if ormP.automacao:
                await self.deleteAutomacao(ormP.nu_cpf, ormP.cliente_id)
                for automacao in ormP.automacao:
                    db_orm = models.AutomacaoUsuario(
                        nu_cpf = ormP.nu_cpf,
                        automacao_id = automacao.id,
                        cliente_id = ormP.cliente_id
                    )        
                    self.db.add(db_orm)

            self.db.commit()
            self.db.refresh(db_orm)
            return db_orm
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def post(self, orm: schemas.Usuario):
        try:
            db_orm = models.Usuario(
                nu_cpf = orm.nu_cpf,
                tx_nome = orm.tx_nome,
                tx_email = orm.tx_email
            )
            self.db.add(db_orm)
            #print(orm.cliente_id)
            for cliente in orm.cliente:
                db_uss = models.UsuarioCliente(
                    nu_cpf = orm.nu_cpf,
                    cliente_id = cliente.id
                )
            
            self.db.add(db_uss)
            self.db.commit()

            self.db.refresh(db_orm)
            return db_orm
        except Exception as error:
            print(traceback.format_exc())
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def senha_acesso(self, orm: schemas.SenhaAcessoUsuario):
        try:
            stmt = update(models.Usuario).where(models.Usuario.nu_cpf == orm.nu_cpf).values(
                nu_cpf = orm.nu_cpf,
                tx_senha = orm.tx_senha
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            return await self.get_by_id(orm.nu_cpf)
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def esqueci_senha(self, orm: schemas.SenhaAcessoUsuario):
        try:
            stmt = update(models.Usuario).where(models.Usuario.nu_cpf == orm.nu_cpf).values(
                nu_cpf = orm.nu_cpf,
                tx_senha = orm.tx_senha
            )
            db_orm = self.db.execute(stmt)
            self.db.commit()
            return True
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def put(self, orm: schemas.Usuario):
        try:
            stmt = update(models.Usuario).where(models.Usuario.nu_cpf == orm.nu_cpf).values(
                nu_cpf = orm.nu_cpf,
                tx_nome = orm.tx_nome,
                tx_foto = orm.tx_foto,
                tx_email = orm.tx_email,
                bo_status = orm.bo_status
            )
            db_orm = self.db.execute(stmt)

            if orm.cliente:
                await self.deleteCliente(orm.nu_cpf)
                for cliente in orm.cliente:
                    db_cliente = models.UsuarioCliente(
                        nu_cpf = orm.nu_cpf,
                        cliente_id = cliente.id,
                    )
                    self.db.add(db_cliente)

            self.db.commit()
            
            return await self.get_by_id(orm.nu_cpf)
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def delete(self, nu_cpf: str):
        try:
            stmt = update(models.Usuario).where(models.Usuario.nu_cpf == nu_cpf).values(
                bo_status = False
            )
            self.db.execute(stmt)
            self.db.commit()
            return {'status': 1, 'message': 'Registro excluido com sucesso.'}
        except Exception as error:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})
            return {'status': 1, 'message': error}

    async def deleteCliente(self, nu_cpf: str):
        try:
            stmt = delete(models.UsuarioCliente).where(models.UsuarioCliente.nu_cpf == nu_cpf)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def deletePerfil(self, nu_cpf: str):
        try:
            stmt = delete(models.PerfilUsuario).where(models.PerfilUsuario.nu_cpf == nu_cpf)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def deleteAutomacao(self, nu_cpf: str, cliente_id: int):
        try:
            stmt = delete(models.AutomacaoUsuario).where(models.AutomacaoUsuario.nu_cpf == nu_cpf).where(models.AutomacaoUsuario.cliente_id == cliente_id)
            self.db.execute(stmt)
            self.db.commit()
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})

    async def redefinirSenha(self, usuario, url):
        from src.providers import hash_provider, token_provider

        try:
            token = await token_provider.gerar_access_token({'sub': usuario.nu_cpf}, 10)

            url = f'''http://{url}/redefinir-senha?nu_cpf={usuario.nu_cpf}&token={token}'''
            
            #return {'access_token': token, 'token_type': "bearer"}
            html = '''<!DOCTYPE html>
                        <html>
                            <head>
                            </head>
                            <style>
                                body, html{
                                    height: 100%;
                                }
                            </style>
                            <body>
                                <div style="min-height: 100%; display: flex; align-items: center; justify-content: center;">
                                    <div style="max-height: 30%;padding: 20px; font-family: "Cereal","Helvetica",Helvetica,Arial,sans-serif; color: #484848; font-size: 24px; line-height: 1.4; text-align: left">
                                        <div style="padding-bottom: 10px;">Olá <b>'''+str(usuario.tx_nome)+'''</b>,</div>
                                        <div style="padding-bottom: 10px;">Recebemos um pedido para redefinir sua senha.</div>
                                        <div style="padding-bottom: 10px;">Se você não tiver feito este pedido, ignore esta mensagem. Caso contrário, você pode redefinir sua senha.</div>
                                        <div style="padding-bottom: 10px; margin-top: 20px;">
                                            <a style="background: #15c; border-radius: 2px; border-radius: 10px; text-align: center; text-decoration: none; color: #FFFFFF; padding: 15px 40px;" href="'''+str(url)+'''">
                                                Redefinir sua senha
                                            </a>
                                        </div>
                                        <div style="padding-bottom: 10px; margin-top: 20px;">Obrigado,</div>
                                        <div style="padding-bottom: 10px;">Equipe Automaxia</div>
                                        <div style="padding-top: 50px; border-bottom: 2px solid rgb(229, 231, 235);"></div>
                                    </div>
                                </div>                                
                            </body>
                        </html>'''
            
            return utils.envio_email('Redefinir senha de acesso', html, usuario.tx_email, arquivos = [])
        except:
            utc_dt = datetime.now(timezone.utc)
            dataErro = utc_dt.astimezone(AMSP)
            utils.grava_error_arquivo({"error": f"""{traceback.format_exc()}""","data": str(dataErro)})