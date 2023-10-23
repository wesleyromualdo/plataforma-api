from datetime import datetime, timezone
import requests
import json
import urllib3

urllib3.disable_warnings()

class ConsoleApi:

    def __init__(self, url):

        self.url = url
        _user = '00000000191'
        _pass = '$2b$12$rfnrdFhgKa7RDiXtxTidU.s5k4yj5W4pFRyg5Zh8w2uzPsNkO92qq'
        self.tokenacesso = str(self.login(_user, _pass)).strip()
        #print(self.tokenacesso)

        self.headers = {'Authorization': 'Bearer ' + self.tokenacesso,'Content-Type': 'application/json'}

    def login(self, _user='', _pass=''):
        try:
            if _user is None or _pass is None:
                return None
            
            headers = {}

            url = str(self.url)+"/login"
            payload = {"username": f"{_user}", "password": f"{_pass}", "client_id": 'api'}
            #payload = json.dumps(payload)

            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            token = response['access_token']
            return token
        except Exception as error:
            return error

    def stop_automacao(self, tarefa_id, bo_status_code=200, tx_resumo='Execução finalizada pela automação'):
        #from datetime import datetime as dthistorico
        #dt.now()
        
        url = str(self.url)+"/tarefa/stop/"

        payload = {
            "tarefa_id": tarefa_id,
            "dt_fim": str(datetime.now(timezone.utc)),
            "bo_status_code": f"{bo_status_code}",
            "tx_resumo": f"{tx_resumo}"
        }
        payload = json.dumps(payload)

        response = self.put(url, payload)
        return response

    def get_start_automacao(self, automacao_id):
        url = str(self.url)+"/tarefa/automacao/"+str(automacao_id)
        response = self.get(url)
        return response

    def gravar_log_execucao(self, historico_tarefa_id, tx_descricao, tx_status="success", tx_acao_auxiliar="", tx_json=""):
        url = str(self.url)+"/logs/"

        payload = {
            "historico_tarefa_id": historico_tarefa_id,
            "tx_status": f"{tx_status}",
            "tx_acao_auxiliar": f"{tx_acao_auxiliar}",
            "tx_descricao": f"{tx_descricao}",
            "tx_json": f"{tx_json}"
        }
        payload = json.dumps(payload)

        response = self.post(url, payload)
        return response

    def gravar_dados_negocial(self, historico_tarefa_id, tx_descricao, dt_fim="", tx_status="", tx_json=""):

        url = str(self.url)+"/dadosnegocial/"

        payload = {
            "historico_tarefa_id": historico_tarefa_id,
            "tx_descricao": f"{tx_descricao}",
            "dt_inicio": str(datetime.now(timezone.utc)),
            "dt_fim": f"{dt_fim}",
            "tx_status": f"{tx_status}",
            "tx_json": f"{tx_json}"
        }

        payload = json.dumps(payload)

        response = self.post(url, payload)
        return response

    def atualizar_dados_negocial(self, id, tx_descricao, historico_tarefa_id="", dt_fim="",tx_status="", tx_json=""):
        url = str(self.url)+"/dadosnegocial/"

        payload = {
            "id": 0,
            "tx_descricao": f"{tx_descricao}"
        }

        if historico_tarefa_id:
            payload.update({"historico_tarefa_id": historico_tarefa_id})

        if dt_fim:
            payload.update({"dt_fim": f"{dt_fim}"})

        if tx_status:
            payload.update({"tx_status": f"{tx_status}"})

        if tx_json:
            payload.update({"tx_json": f"{tx_json}"})

        payload = json.dumps(payload)

        response = self.put(url, payload)
        return response

    def get(self, url):
        try:
            response = requests.request("GET", url, headers=self.headers, data="")
            return response.json()
        except Exception as error:
            return error

    def put(self, url, payload):
        try:
            response = requests.request("PUT", url, headers=self.headers, data=payload)
            return response.json()
        except Exception as error:
            return error

    def post(self, url, payload):
        try:
            response = requests.request("POST", url, headers=self.headers, data=payload)
            
            if( 'detail' not in response.json() and response.json() is not None):
                response = {'message': 'Registro inserido com sucesso!', 'id': response.json()['id']}
            else:
                response = response.json()
            return response
        except Exception as error:
            return error