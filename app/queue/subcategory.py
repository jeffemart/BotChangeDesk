
import requests
import logging
import json
import os
from dotenv import load_dotenv
from app.auth.authenticate import Auth

# Configurar o logger
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)


class SubcategoryListing:
    def __init__(self):
        self.token = os.getenv('TOKEN')
        self.header = {'Authorization': f'{self.token}'}
        self.refresh_token()

    def refresh_token(self):
        # if not self.token:  # Atualiza apenas se o token não estiver definido
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
            response.raise_for_status()
            response_data = response.json()

            # Adicione logs para detalhes da solicitação e resposta
            logging.info(f"API Request to {url} with params: {params}")

            if response_data != {'erro': 'Token expirado ou não existe'}:
                return response_data
            else:
                logging.warning("Token expired or not available.")
                return None

        except requests.RequestException as e:
            logging.error(f"Error in API request: {e}")
            raise

    def get_subcategory_list(self):
        url = 'https://api.desk.ms/SubCategorias/lista'
        parameters = {
            "Pesquisa": "",
            "Ativo": "S",
            "Ordem": [
                {
                    "Coluna": "SubCategoria",
                    "Direcao": "true"
                }
            ]
        }

        try:
            response_data = self.make_api_request(url, parameters)

            if response_data:
                logging.info("Subcategory list obtained successfully")

                # Process the response_data as needed

                # Save response_data to a JSON file
                self.save_to_json(response_data, 'subcategory_list.json')

                return response_data
            else:
                logging.warning("Failed to obtain subcategory list.")
                return None

        except requests.HTTPError as http_err:
            if http_err.response.status_code == 401:
                logging.warning(
                    "Token expired. Refreshing token and retrying...")
                # Adicione a lógica para atualizar o token, se necessário
                return self.get_subcategory_list()  # Tentar novamente após a atualização do token
            else:
                logging.error("HTTPError: %s", http_err)
                raise  # Rethrow the exception after logging
        except Exception as e:
            logging.error("Error: %s", e)
            raise  # Rethrow the exception after logging

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
