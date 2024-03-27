import schedule
import time
import console_api

import random
import string

tamanho = 8
valores = string.ascii_letters
senha = ''
for i in range(tamanho):
  senha += random.choice(valores)

print(senha)


class ApiService:

    def __init__(self, url):
        self.log_id = ''
        self.dadosnegocial_id = ''
        self.tarefa_id = ''
        self.console = console_api.ConsoleApi(url)

    def gravar_logs(self, json_log):
        retorno = self.console.gravar_log_execucao(json_log)
        self.log_id = retorno['id']
        print(retorno, self.log_id)

    def gravar_dados_negocial(self, json_dados):
        retorno = self.console.gravar_dados_negocial(json_dados)
        self.dadosnegocial_id = retorno['id']
        print(retorno, self.dadosnegocial_id)

    def atualizar_dados_negocial(self, json_dados):
        retorno = self.console.atualizar_dados_negocial(json_dados['id'], json_dados['tx_descricao'], json_dados['historico_tarefa_id'], json_dados['dt_fim'], json_dados['tx_status'], json_dados['tx_json'])
        #self.dadosnegocial_id = retorno['id']
        print(retorno, self.dadosnegocial_id)

    def get_execucao_automacao(self, automacao_id):
        retorno = self.console.get_start_automacao(automacao_id)
        print('VERIFICANDO...')
        print(retorno)

        if 'automacao_id' in retorno:
            print('INCIANDO A EXECUÇÃO DA AUTOMAÇÃO: '+str(retorno['automacao_id'])+' - '+str(retorno['tx_nome']))
            
            #APÓS A EXECUÇÃO DA AUTOMAÇÃO, É NECESSÁRIO CHAMAR A FUNÇÃO ABAIXO PARA FINALIZAR A EXECUÇÃO.
            # PARAMETROS
            # tarefa_id - Obrigatório
            # bo_status_code - Opcional, default 200
            # tx_resumo  - Opcional, default 'Execução finalizada pela automação'
            # stop_automacao(tarefa_id, bo_status_code, tx_resumo)
            
            self.console.stop_automacao(retorno['id'], '', '')
        return retorno

    def agendamento(self, automacao_id):
        schedule.every(5).seconds.do( self.get_execucao_automacao, automacao_id )

        while True:
            print('Aguardandoção...')
            schedule.run_pending()
            time.sleep(1)


api = ApiService('http://localhost:8000')

from datetime import datetime, timezone
json_dados_update = {
    "id": 0,
    "historico_tarefa_id": 23,
    "tx_descricao": "",
    "dt_inicio": str(datetime.now(timezone.utc)),
    "dt_fim": "",
    "tx_status": "",
    "tx_json": ""
}
#api.atualizar_dados_negocial(json_dados)

json_dados = {
    "historico_tarefa_id": 23,
    "tx_descricao": "",
    "dt_inicio": str(datetime.now(timezone.utc)),
    "dt_fim": "",
    "tx_status": "",
    "tx_json": ""
}
#api.gravar_dados_negocial(json_dados)

json_log = {
        "historico_tarefa_id": 23,
        "tx_status": "success",
        "tx_descricao": "teste 2",
        "tx_json": "teste 3"
    }
#api.gravar_logs(json_log)

#agendamento(1)

#start Python C:/Users/User/Desktop/teste.py

import winreg as reg  
import os              
  
def AddToRegistry(): 

    pth = os.path.dirname(os.path.realpath(__file__))
    print(pth)
    s_name="example_api.py"
    address=pth+'/'+s_name
    key_value = "Software\Microsoft\Windows\CurrentVersion\Run"
    open = reg.OpenKey('HKEY_CURRENT_USER',key_value,0,reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open,"any_name",0,reg.REG_SZ,address)
    reg.CloseKey(open) 
if __name__=="__main__": 
    AddToRegistry() 