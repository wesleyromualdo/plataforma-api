# ConsoleApi

Backend da console para execução das automações.

## 🚀 Começando


```
cd existing_repo
git remote add origin https://gitlab.zello.services/clientes/rpa/consoleapi.git
git branch -M main
git push -uf origin main
```

### 📋 Pré-requisitos

De que coisas você precisa para instalar o software e como instalá-lo?

```
Ter o arquivo console_api.py no diretório raiz da automação.
    * https://gitlab.zello.services/clientes/rpa/consoleapi/-/blob/develop/console_api.py
```

### 🔧 Instalação

Segue o passo-a-passo para a utilização da ferramenta no projeto.

```
Inicie a execução da automação chamando a função abaixo:
import console_api

def get_execucao_automacao(automacao_id):
    retorno = console_api.get_start_automacao(automacao_id)
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
        
        console_api.stop_automacao(retorno['id'], '', '')
    return retorno

def agendamento(self, automacao_id):
    schedule.every(5).seconds.do( self.get_execucao_automacao, automacao_id )

    while True:
        print('Aguardandoção...')
        schedule.run_pending()
        time.sleep(1)

```

## 🛠️ Construído com

* [Python](https://www.python.org/downloads/) - Linguagem Open-Source do back-end
* [SQLAlchemy](https://www.sqlalchemy.org/) - ORM que fornece flexibilidade total do SQL.
* [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Ferramenta de migração de banco de dados.
* [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno, rápido (de alto desempenho) para construir APIs com Python.

## ✒️ Autores

Mencione todos aqueles que ajudaram a levantar o projeto desde o seu início

* **Wesley Romualdo da Silva** - *Trabalho Inicial*
