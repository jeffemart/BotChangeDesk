import requests
import logging
import json
import os
from dotenv import load_dotenv

class Auth:
    def __init__(self, url='https://api.desk.ms/Login/autenticar'):
        self.__token = ''
        self.url = url
        load_dotenv()  # Carregar variáveis de ambiente a partir do arquivo .env

    def token(self) -> str:
        # Recuperar credenciais do ambiente
        authorization = os.getenv('AUTHORIZATION')
        public_key = os.getenv('PUBLICKEY')

        if not authorization or not public_key:
            logging.warning("As variáveis de ambiente AUTHORIZATION ou PUBLICKEY estão ausentes.")
            return

        header = {'Authorization': authorization, 'content-type': 'application/json'}
        params = json.dumps({'PublicKey': public_key})

        response = requests.post(self.url, headers=header, data=params)
        logging.debug(response)

        if response.status_code == 200:
            self.__token = response.json()
        else:
            logging.warning("Falha na requisição do token")

    def get_token(self):
        return self.__token