from dotenv import dotenv_values
import os, subprocess

variavel = dotenv_values(".env")

print( os.getenv("DATABASE_URL_SOLVER") )
quit()

for var, val in variavel.items():
    os.system(f'setx {var} "{val}"')
    #subprocess.run(f'set {var} "{val}"', shell=True)
    print(f'setx {var} "{val}"')

'''
setx PG_USER_SOLVER "botsolve"
setx PG_PASS_SOLVER "bot!solve!"
set PG_DB_SOLVER "SolveAutomation"
set DATABASE_URL_SOLVER "postgresql+psycopg2://botsolve:bot!solve!@rpa-dsv-postgres.api.zello.services:5446/SolveAutomation"
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
set URL_FRONT_SOLVER "https://consoleapi-dsv.api.zello.services"
set URL_BACK_SOLVER "https://consoleapi-dsv.api.zello.services"
'''