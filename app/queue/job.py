import threading
import time
import requests
import json
from datetime import datetime, timedelta
from app.auth.authenticate import Auth
import logging

# Configurar o logger no script listing
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)


class JobThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.header = None

    def run(self):
        while not self._stop_event.is_set():
            # Trecho de código a ser executado
            try:
                self.process_tickets()
            except Exception as e:
                logging.error("Erro ao processar tickets: %s", e)

            time.sleep(30)  # Tempo de espera entre as iterações

    def stop(self):
        self._stop_event.set()

    def process_tickets(self):
        url = 'https://api.desk.ms/ChamadosSuporte/lista'
        parameters = json.dumps({
            "Pesquisa": "",
            "Tatual": "",
            "Ativo": "NaFila",
            "StatusSLA": "N",
            "Colunas":
            {
                "Chave": "on",
                "CodChamado": "on",
                "NomePrioridade": "on",
                "DataCriacao": "on",
                "HoraCriacao": "on",
                "DataFinalizacao": "on",
                "HoraFinalizacao": "on",
                "DataAlteracao": "on",
                "HoraAlteracao": "on",
                "NomeStatus": "on",
                "Assunto": "on",
                "Descricao": "on",
                "ChaveUsuario": "on",
                "NomeUsuario": "on",
                "SobrenomeUsuario": "on",
                "NomeOperador": "on",
                "SobrenomeOperador": "on",
                "TotalAcoes": "on",
                "TotalAnexos": "on",
                "Sla": "on",
                "CodGrupo": "on",
                "NomeGrupo": "on",
                "CodSolicitacao": "on",
                "CodSubCategoria": "on",
                "CodTipoOcorrencia": "on",
                "CodCategoriaTipo": "on",
                "CodPrioridadeAtual": "on",
                "CodStatusAtual": "on"
            },
            "Ordem": [
                {
                    "Coluna": "Chave",
                    "Direcao": "true"
                }
            ]
        })

        try:
            response_data = self.make_api_request(url, parameters)
            logging.info("Requisição bem-sucedida")

            if response_data:
                for item in response_data:
                    if item.get("Assunto") in ["Sistemas - Gestão - ERP - Cadastro de Endereços - Cadastrar", "Sistemas - Gestão - OTTs - Watch Brasil - Sem Acesso"]:
                        self.process_item(item)

            else:
                logging.info("Nenhum ticket encontrado.")

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logging.warning(
                    "Token expirado. Atualizando token e tentando novamente...")
                self.refresh_token()
                self.process_tickets()
            else:
                logging.error("HTTPError: %s", http_err)

        except Exception as e:
            logging.error("Erro ao processar tickets: %s", e)

    def process_item(self, item):
        logging.info("Processando item com Assunto: %s", item.get("Assunto"))

        Parametros_Interacao = {
            "Chave": item["CodChamado"],
            "TChamado": {
                "CodFormaAtendimento": "9",
                "CodStatus": "0000006",
                "CodAprovador": [""],
                "TransferirOperador": "",
                "TransferirGrupo": "",
                "CodTerceiros": "",
                "Protocolo": "",
                "Descricao": "O Chamado está em Andamento e está sendo tratado por nossa equipe, favor aguardar maiores informações.",
                "CodAgendamento": "",
                "DataAgendamento": "",
                "HoraAgendamento": "",
                "CodCausa": "",
                            "CodOperador": "",
                            "CodGrupo": "",
                            "EnviarEmail": "S",
                            "EnvBase": "N",
                            "CodFPMsg": "1387",
                            "DataInteracao": datetime.now().strftime("%d-%m-%Y"),
                            "HoraInicial": datetime.now().strftime("%H:%M:%S"),
                            "HoraFinal": (datetime.now() + timedelta(minutes=1)).strftime("%H:%M"),
                            "SMS": "",
                            "ObservacaoInterna": "",
                            "PrimeiroAtendimento": "N",
                            "SegundoAtendimento": "N"
            },
            "TIc": {
                "Chave": {
                    "278": "off",
                    "280": "off"
                }
            }
        }

        try:
            response = requests.put("https://api.desk.ms/ChamadosSuporte/interagir",
                                    headers=self.header, json=Parametros_Interacao)
            logging.info(response)

            if response.status_code == 200:
                with open('interacao.json', 'w', encoding='utf8') as resultado:
                    json.dump(response.json(), resultado,
                              indent=4, ensure_ascii=False)
                logging.info("Interação bem-sucedida")
            else:
                logging.error(
                    "Falha na requisição. Código de status: %s", response.status_code)

        except requests.RequestException as e:
            logging.error("Erro na requisição: %s", e)

    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()
            return response.json().get("root", [])
        except requests.RequestException as e:
            logging.error("Erro na requisição da API: %s", e)
            raise

    def refresh_token(self):
        auth_instance = Auth()
        obtained_token = auth_instance.token()
        if obtained_token:
            print(f"Obtained token: {obtained_token}")
            self.token = obtained_token
            self.header = {'Authorization': f'{self.token}'}
        else:
            print("Failed to obtain token.")

