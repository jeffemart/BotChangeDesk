import threading
import requests
import logging
import json
import time
import os

from datetime import datetime, timedelta
from app.auth.authenticate import Auth
from app.queue.listing import Listing


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
        self.listing_instance = Listing()

    def run(self):
        while not self._stop_event.is_set():
            try:
                self.process_tickets()
            except Exception as e:
                logging.error(f"{os.path.basename(__file__)}: Erro ao processar tickets: %s", e)

            time.sleep(30)  # Tempo de espera entre as iterações


    def stop(self):
        self._stop_event.set()


    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()
            return response.json().get("root", [])
        except requests.RequestException as e:
            logging.error(f"{os.path.basename(__file__)}: Erro na requisição da API: %s", e)
            raise
     
        
    def process_tickets(self):
        try:
            get_listing = self.listing_instance.get_ticket_list()
            bot_list = get_listing

            if bot_list:
                for item in bot_list:
                    if item.get("Assunto") in ["Sistemas - Gestão - ERP - Cadastro de Endereços - Cadastrar", "Sistemas - Gestão - OTTs - Watch Brasil - Sem Acesso"]:
                        self.process_item(item)
                    else:
                        pass
            else:
                logging.info(f"{os.path.basename(__file__)}: Nenhum ticket encontrado.")

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logging.warning(
                    f"{os.path.basename(__file__)}: Token expirado. Atualizando token e tentando novamente...")
            else:
                logging.error(f"{os.path.basename(__file__)}: HTTPError: %s", http_err)

        except Exception as e:
            logging.error(f"{os.path.basename(__file__)}: Erro ao processar tickets: %s", e)


    def process_item(self, item):
        logging.info(f"{os.path.basename(__file__)}: Processando item com Assunto: %s", item.get("Assunto"))

        Parametros_Interacao = {
            "Chave": item.get("CodChamado"),
            "TChamado": {
                "CodFormaAtendimento": "9",
                "CodStatus": "6",
                "CodAprovador": "",
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
                "DataInteracao": f"{datetime.now().strftime("%d-%m-%Y")}",
                "HoraInicial": f"{datetime.now().strftime("%H:%M")}",
                "HoraFinal": f"{(datetime.now() + timedelta(minutes=1)).strftime("%H:%M")}",
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

        logging.info(f"{os.path.basename(__file__)}: Parametros_Interacao")
        try:
            response = requests.put("https://api.desk.ms/ChamadosSuporte/interagir", headers={'Authorization': f'{self.listing_instance.token}'}, json=Parametros_Interacao)
            logging.info(f"{os.path.basename(__file__)}: {response}")
            logging.info(f"{os.path.basename(__file__)}: {response.json()}")
            
            if response.json() != {'erro': 'Token expirado ou não existe'}:
                json_response = response.json()
                with open('interacao.json', 'w', encoding='utf8') as resultado:
                    json.dump(json_response, resultado, indent=4, ensure_ascii=False)
                logging.info(f"{os.path.basename(__file__)}: Interação bem-sucedida")
            else:
                logging.error(f"{os.path.basename(__file__)}: Falha na requisição. Código de status: %s", response.json())

        except requests.RequestException as e:
            logging.error(f"{os.path.basename(__file__)}: Erro na requisição: %s", e)

