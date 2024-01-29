import requests
import logging
import json
from datetime import datetime
from app.auth.authenticate import Auth



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
            self.header = {'Authorization': f'Bearer {self.token}'}
        else:
            print("Failed to obtain token.")

    def make_api_request(self, url, params):
        try:
            response = requests.post(url, headers=self.header, data=params)
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
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
            # Process the response_data as needed
            print("Requisition successful")
            logging.info("Requisition successful")
        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:  # Unauthorized (token expired)
                logging.warning("Token expired. Refreshing token and retrying...")
                self.refresh_token()
                self.get_ticket_list()  # Retry the API request after token refresh
            else:
                logging.error("HTTPError: %s", http_err)
        except Exception as e:
            print(f"Error: {e}")
            logging.error("Error: %s", e)


if __name__ == "__main__":
    listing_instance = Listing()
    listing_instance.get_ticket_list()