import requests
import logging
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from app.auth.authenticate import Auth

# Configurar o logger no script listing
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)


class Listing:
    def __init__(self):
        # Substitua 'SEU_TOKEN' pelo nome real da variável de ambiente
        self.token = os.getenv('TOKEN')
        self.header = {'Authorization': f'{self.token}'}
        self.refresh_token()

    def refresh_token(self):
        if not self.token:  # Atualiza apenas se o token não estiver definido
            auth_instance = Auth()
            obtained_token = auth_instance.token()
            if obtained_token:
                logging.info(f"Token updated successfully: {obtained_token}")
                self.token = obtained_token
                self.header = {'Authorization': f'{self.token}'}
            else:
                logging.warning("Failed to obtain token.")

    def refresh_new_token(self):
        auth_instance = Auth()
        obtained_token = auth_instance.token()
        if obtained_token:
            logging.info(f"Token updated successfully: {obtained_token}")
            self.token = obtained_token
            self.header = {'Authorization': f'{self.token}'}
        else:
            logging.warning("Failed to obtain token.")

    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            response_data = response.json()

            # Adicione logs para detalhes da solicitação e resposta
            logging.info(
                f"{response} - API Request to {url} with params: {params}")

            if response_data != {'erro': 'Token expirado ou não existe'}:
                return response_data["root"]
            else:
                logging.warning("Token expired or not available.")
                return None  # Não chame recursivamente aqui

        except requests.RequestException as e:
            logging.error(f"Error in API request: {e}")
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

            if response_data:
                logging.info("Requisition successful")

                # Process the response_data as needed
                print("Executou a lista!")
                return response_data
            else:
                logging.warning("Failed to obtain ticket list.")
                self.refresh_new_token()
                return None

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logging.warning(
                    "Token expired. Refreshing token and retrying...")
                self.refresh_token()
                return None  # Retry the API request after token refresh
            else:
                logging.error("HTTPError: %s", http_err)
                raise  # Rethrow the exception after logging
