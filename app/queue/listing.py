import requests
import logging
import json
from datetime import datetime
from app.auth.authenticate import Auth

# Configurar o logger no script listing
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)


class Listing:
    def __init__(self):
        self.token = None
        self.header = None
        self.refresh_token()

    def refresh_token(self):
        auth_instance = Auth()
        obtained_token = auth_instance.token()
        if obtained_token:
            print(f"Obtained token: {obtained_token}")
            self.token = obtained_token
            self.header = {'Authorization': f'{self.token}'}
        else:
            print("Failed to obtain token.")

    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()["root"]
        except requests.RequestException as e:
            logging.error("Error in API request: %s", e)
            raise

    def get_ticket_list(self):
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
            print("Requisition successful")
            logging.info("Requisition successful")

            # Process the response_data as needed
            if response_data:
                ticket_list = [ticket.get("Assunto", "") for ticket in response_data]
                return "\n".join(ticket_list)
            else:
                return "Nenhum ticket encontrado."

        except requests.HTTPError as http_err:
            # Unauthorized (token expired)
            if http_err.response.status_code == 401:
                logging.warning(
                    "Token expired. Refreshing token and retrying...")
                self.refresh_token()
                self.get_ticket_list()  # Retry the API request after token refresh
            else:
                logging.error("HTTPError: %s", http_err)
        except Exception as e:
            print(f"Error: {e}")
            logging.error("Error: %s", e)
