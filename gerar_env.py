from dotenv import dotenv_values
import os, subprocess

variavel = dotenv_values(".env")

print( os.getenv("DATABASE_URL_AUTOMAXIA") )
quit()

for var, val in variavel.items():
    os.system(f'setx {var} "{val}"')
    #subprocess.run(f'set {var} "{val}"', shell=True)
    print(f'setx {var} "{val}"')

'''
setx PG_USER_AUTOMAXIA="usr_plataforma"
setx PG_PASS_AUTOMAXIA="0503b06b-8a2f-e5aa-4f7f-ad5a5a03fffc"
set PG_DB_AUTOMAXIA "plataforma"
set DATABASE_URL_AUTOMAXIA "postgresql+psycopg2://usr_plataforma:0503b06b-8a2f-e5aa-4f7f-ad5a5a03fffc@production-plataforma-api.cluster-ceikcskujn3o.us-east-1.rds.amazonaws.com:5432/plataforma"
set KEEPALIVES "1"
set KEEPALIVES_IDLE "30"
set KEEPALIVES_INTERVAL "10"
set KEEPALIVES_COUNT "5"
set POOL_SIZE "10"
set MAX_OVERFLOW "20"
set AUTOCOMMIT "False"
set AUTOFLUSH "False"
set EXPIRE_ON_COMMIT "True"
set FUTURE "True"
set URL_FRONT_AUTOMAXIA "https://plataforma.automaxia.com.br"
set URL_BACK_AUTOMAXIA "https://plataforma-api.automaxia.com.br"
'''