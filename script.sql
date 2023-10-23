--senha = admin@solve
INSERT INTO public.usuario(nu_cpf, tx_nome, tx_senha, tx_email, bo_status, dt_inclusao)
VALUES('00000000191', 'Administrador Solve', '$2b$12$rfnrdFhgKa7RDiXtxTidU.s5k4yj5W4pFRyg5Zh8w2uzPsNkO92qq', 'roborpabsb@gmail.com', true, now());

INSERT INTO public.setor(tx_sigla, tx_nome, bo_status)
VALUES('Solve', 'Área responsável pela execução e configuração inicial da ferramenta', true);

INSERT INTO public.perfil(tx_nome, tx_finalidade, bo_superuser, bo_status)
VALUES('Administrador', 'Responsável gerir os cadastros e configuração da ferramenta', true, true);

INSERT INTO public.usuario_setor(nu_cpf, setor_id)
VALUES('00000000191', (SELECT id FROM setor s WHERE tx_sigla = 'Solve'));

INSERT INTO public.perfil_usuario(nu_cpf, perfil_id)
VALUES('00000000191', (SELECT id FROM public.perfil WHERE tx_nome = 'Administrador'));

#senha = admin@solve

INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(1000, 'Dashboard', '/dashboard', 'dashboard', 1, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(2000, 'Tarefa', '/tarefa', 'assignment', 2, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(3000, 'Gestão de automação', '/automacao', 'settings', 3, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(4000, 'Gestão de usuário', '/usuario', 'group', 4, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(5000, 'Cadastro de Módulo', '/modulo', 'view_module', 5, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(6000, 'Cadastro de Perfil', '/perfil', 'assignment_ind', 6, true);
INSERT INTO public.menu(nu_codigo, tx_nome, tx_link, tx_icon, nu_ordem, bo_status) VALUES(7000, 'Cadastro de Setor', '/setor', 'supervised_user_circle', 7, true);

INSERT INTO public.perfil_menu(menu_id, perfil_id, setor_id)
(SELECT id, (SELECT id FROM public.perfil WHERE tx_nome = 'Administrador'), (SELECT id FROM public.setor WHERE tx_sigla = 'Solve') FROM public.menu);

CREATE OR REPLACE FUNCTION public.removeacento(character varying)
 RETURNS character varying
 LANGUAGE sql
 IMMUTABLE
AS $function$
SELECT TRANSLATE($1, 'áéíóúàèìòùãõâêîôôäëïöüçÁÉÍÓÚÀÈÌÒÙÃÕÂÊÎÔÛÄËÏÖÜÇ-',
'aeiouaeiouaoaeiooaeioucAEIOUAEIOUAOAEIOOAEIOUC ')
$function$
;


CREATE OR REPLACE FUNCTION public.datediff(units character varying, start_t timestamp without time zone, end_t timestamp without time zone)
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
;
