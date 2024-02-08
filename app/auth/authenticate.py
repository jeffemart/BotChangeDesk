import os
import json
import logging
import requests

from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key

# Configurar o logger no script listing
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)


class Auth:
    def __init__(self, url='https://api.desk.ms/Login/autenticar'):
        self.__token = ''
        self.url = url

        # Load environment variables from the .env file
        load_dotenv()

    def token(self) -> str:
        # Retrieve credentials from the environment
        authorization = os.getenv('AUTHORIZATION')
        public_key = os.getenv('PUBLICKEY')

        if not authorization or not public_key:
            logging.warning(
                f"{os.path.basename(__file__)}: The environment variables AUTHORIZATION or PUBLICKEY are missing.")
            return None

        header = {'Authorization': os.getenv(
            'AUTHORIZATION'), 'content-type': 'application/json'}
        params = json.dumps({'PublicKey': public_key})

        try:
            with requests.Session() as session:
                response = session.post(self.url, headers=header, data=params)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                self.__token = response.json()
                logging.debug(f"{os.path.basename(__file__)}: Token acquisition successful")
                print(f"{datetime.now().strftime("%H:%M:%S")} - Token acquisition: {self.__token}")

                # Save the token in the .env file
                set_key('./app/.env', 'TOKEN', self.__token)

                return self.__token
        except requests.RequestException as e:
            logging.warning(f"{os.path.basename(__file__)}: Token acquisition failed. Error: %s", e)
            return None

    def get_token(self):
        return self.__token
