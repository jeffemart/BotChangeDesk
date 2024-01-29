import requests
import logging
import json
import os
from dotenv import load_dotenv, set_key

class Auth:
    def __init__(self, url='https://api.desk.ms/Login/autenticar'):
        self.__token = ''
        self.url = url
        load_dotenv()  # Load environment variables from the .env file

    def token(self) -> str:
        # Retrieve credentials from the environment
        authorization = os.getenv('AUTHORIZATION')
        public_key = os.getenv('PUBLICKEY')

        if not authorization or not public_key:
            logging.warning("The environment variables AUTHORIZATION or PUBLICKEY are missing.")
            return None

        header = {'Authorization': os.getenv('AUTHORIZATION'), 'content-type': 'application/json'}
        params = json.dumps({'PublicKey': public_key})

        try:
            with requests.Session() as session:
                response = session.post(self.url, headers=header, data=params)
                response.raise_for_status()  # Raise an HTTPError for bad responses

                self.__token = response.json()
                logging.debug("Token acquisition successful")

                # Save the token in the .env file
                set_key('./app/.env', 'TOKEN', self.__token)

                return self.__token
        except requests.RequestException as e:
            logging.warning("Token acquisition failed. Error: %s", e)
            return None

    def get_token(self):
        return self.__token

if __name__ == "__main__":
    auth_instance = Auth()
    obtained_token = auth_instance.token()
    if obtained_token:
        print(f"Obtained token: {obtained_token}")
    else:
        print("Failed to obtain token.")
