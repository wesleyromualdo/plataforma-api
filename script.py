import os
import psycopg2
import shutil, traceback

class Configuracao():

    def __init__(self):
      try:
        os.system("alembic init alembic")
        shutil.copy('env_alembic.py', 'alembic/env.py')
        os.system('alembic revision --autogenerate -m "Criando tabelas no banco de dados"')
        os.system('alembic upgrade head')

        self.conecta_db()
      except Exception as erro:
        shutil.copy('env_alembic.py', 'alembic/env.py')
        print(erro)

    def conecta_db(self):
      try:
        self.con = psycopg2.connect(host='154.38.187.212', port="6432", database='plataforma', user='usr_plataforma', password='cG9zdGdyZXNOPRTfcGFzc3dvcmQ454aaaff')
        self.cur = self.con.cursor()
      except:
        print(traceback.format_exc())

    def inserir_db(self):
        try:
            #admin@automaxia
            sql = "INSERT INTO public.usuario(nu_cpf, tx_nome, tx_senha, tx_email, bo_status, dt_inclusao) VALUES('05646593638', 'Administrador Automaxia', '$2b$12$U7nJOqm/AwKu0WuIpx/6weZFQ7bDcxfMsnblhXat31YXqBomPkiV6', 'wesleyromualdo@gmail.com', true, now());"
            self.cur.execute(sql)

            sql = "INSERT INTO public.cliente(tx_sigla, tx_nome, bo_status) VALUES('Automaxia', 'Área responsável pela execução e configuração inicial da ferramenta', true);"
            self.cur.execute(sql)

            sql = "INSERT INTO public.perfil(tx_nome, tx_finalidade, bo_superuser, bo_status, bo_delegar, constante_virtual) VALUES('Administrador', 'Responsável gerir os cadastros e configuração da ferramenta', true, true, true, 'ADMINISTRADOR');"
            self.cur.execute(sql)

            sql = "INSERT INTO public.perfil(tx_nome, tx_finalidade, bo_superuser, bo_status, bo_delegar, constante_virtual) VALUES('Workers', 'Esse perfil tem a finalidade de executar os script python', false, true, false, 'ROBO_EXECUTOR');"
            self.cur.execute(sql)

            sql = "INSERT INTO public.usuario_cliente(nu_cpf, cliente_id) VALUES('05646593638', (SELECT id FROM cliente s WHERE tx_sigla = 'Automaxia'));"
            self.cur.execute(sql)

            sql = "INSERT INTO public.perfil_usuario(nu_cpf, perfil_id) VALUES('05646593638', (SELECT id FROM public.perfil WHERE tx_nome = 'Administrador'));"
            self.cur.execute(sql)

            sql = """INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(1000, 'Dashboard', '/dashboard', 'dashboard', 1, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(2000, 'Tarefa', '/tarefa', 'assignment', 2, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(3000, 'Gestão de automação', '/automacao', 'settings', 3, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(4000, 'Gestão de usuário', '/usuario', 'group', 4, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(5000, 'Cadastro de Módulo', '/modulo', 'view_module', 5, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(6000, 'Cadastro de Perfil', '/perfil', 'assignment_ind', 6, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(7000, 'Cadastro de cliente', '/cliente', 'supervised_user_circle', 7, true);
            """
            self.cur.execute(sql)

            sql = "INSERT INTO public.perfil_menu(menu_id, perfil_id, cliente_id) (SELECT id, (SELECT id FROM public.perfil WHERE tx_nome = 'Administrador'), (SELECT id FROM public.cliente WHERE tx_sigla = 'Automaxia') FROM public.menu);"
            self.cur.execute(sql)

            sql = """CREATE OR REPLACE FUNCTION public.removeacento(character varying)
 RETURNS character varying
 LANGUAGE sql
 IMMUTABLE
AS $function$
SELECT TRANSLATE($1, 'áéíóúàèìòùãõâêîôôäëïöüçÁÉÍÓÚÀÈÌÒÙÃÕÂÊÎÔÛÄËÏÖÜÇ-',
'aeiouaeiouaoaeiooaeioucAEIOUAEIOUAOAEIOOAEIOUC ')
$function$
;"""
            self.cur.execute(sql)

            sql = """CREATE OR REPLACE FUNCTION public.datediff(units character varying, start_t timestamp without time zone, end_t timestamp without time zone)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
   DECLARE
     diff_interval INTERVAL;
     diff INT = 0;
     years_diff INT = 0;
   BEGIN
     IF units IN ('yy', 'yyyy', 'year', 'mm', 'm', 'month') THEN
       years_diff = DATE_PART('year', end_t) - DATE_PART('year', start_t);

       IF units IN ('yy', 'yyyy', 'year') THEN
         -- SQL Server does not count full years passed (only difference between year parts)
         RETURN years_diff;
       ELSE
         -- If end month is less than start month it will subtracted
         RETURN years_diff * 12 + (DATE_PART('month', end_t) - DATE_PART('month', start_t));
       END IF;
     END IF;

     -- Minus operator returns interval 'DDD days HH:MI:SS'
     diff_interval = end_t - start_t;

     diff = diff + DATE_PART('day', diff_interval);

     IF units IN ('wk', 'ww', 'week') THEN
       diff = diff/7;
       RETURN diff;
     END IF;

     IF units IN ('dd', 'd', 'day') THEN
       RETURN diff;
     END IF;

     diff = diff * 24 + DATE_PART('hour', diff_interval);

     IF units IN ('hh', 'hour') THEN
        RETURN diff;
     END IF;

     diff = diff * 60 + DATE_PART('minute', diff_interval);

     IF units IN ('mi', 'n', 'minute') THEN
        RETURN diff;
     END IF;

     diff = diff * 60 + DATE_PART('second', diff_interval);

     RETURN diff;
   END;
   $function$
;"""
            self.cur.execute(sql)

            self.con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            self.con.rollback()
            self.cur.close()
            return 1
        self.cur.close()

ob = Configuracao()
retorno = ob.inserir_db()