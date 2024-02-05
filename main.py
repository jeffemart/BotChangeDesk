import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv

from app.auth.authenticate import Auth
from app.queue.listing import Listing
from app.queue.job import JobThread
from app.queue.subcategory import SubcategoryListing

# Carregar variáveis de ambiente do arquivo .env que está dentro do diretório app
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', '.env'))

# Configurar o logger
logging.basicConfig(filename='bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Adicionar um manipulador de logs para enviar mensagens de erro para a saída padrão (console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)

# Obter o token do ambiente
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Inicializar o bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Criar uma instância da classe Listing
listing_call = Listing()

# Comando /start para exibir o menu
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Iniciar Job", callback_data='start_job')
    item2 = types.InlineKeyboardButton("Parar Job", callback_data='stop_job')
    item3 = types.InlineKeyboardButton("Lista", callback_data='list_ticket')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)

# Tratamento das opções do menu embutido
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_menu_options(call):
    if call.data == 'start_job':
        # Lógica para iniciar o job
        if not hasattr(bot, 'job_thread') or not bot.job_thread.is_alive():
            bot.job_thread = JobThread()
            bot.job_thread.start()
            bot.send_message(call.message.chat.id, "Job iniciado!")
        else:
            bot.send_message(call.message.chat.id, "O job já está em execução.")
    elif call.data == 'stop_job':
        # Lógica para parar o job
        if hasattr(bot, 'job_thread') and bot.job_thread.is_alive():
            bot.job_thread.stop()
            bot.job_thread.join()
            bot.send_message(call.message.chat.id, "Job interrompido.")
        else:
            bot.send_message(call.message.chat.id, "O job não está em execução.")
    elif call.data == 'list_ticket':
        try:
            # Tentar obter a lista de tickets
            get_listing = listing_call.get_ticket_list()
            bot_list = get_listing  # Não use .json() aqui, pois a função já retorna o resultado processado

            # Processar a lista de tickets
            if bot_list:
                ticket_list = [ticket.get("Assunto", "") for ticket in bot_list]
                formatted_ticket_list = "\n".join(ticket_list)
                bot.send_message(call.message.chat.id, formatted_ticket_list)
            else:
                bot.send_message(call.message.chat.id, "Nenhum ticket encontrado.")
        except Exception as e:
            # Lidar com exceções que podem ocorrer durante a obtenção da lista de tickets
            bot.send_message(call.message.chat.id, f"Erro ao obter a lista de tickets: {e}")

def main():
    # Verificar se todas as variáveis de ambiente necessárias estão definidas
    if not TELEGRAM_BOT_TOKEN:
        logging.error("Certifique-se de definir a variável de ambiente TELEGRAM_BOT_TOKEN no arquivo .env")
        return

    # Iniciar o bot
    bot.polling()

if __name__ == '__main__':
    main()
