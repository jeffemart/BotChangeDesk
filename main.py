import os
import logging
import telebot
from telebot import types
from dotenv import load_dotenv
from app.auth.authenticate import Auth

# Carregar variáveis de ambiente do arquivo .env que está dentro do diretório app
load_dotenv(os.path.join(os.path.dirname(__file__), 'app', '.env'))

# Obter o token do ambiente
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Inicializar o bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Comando /start para exibir o menu
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Opção 1", callback_data='option_1')
    item2 = types.InlineKeyboardButton("Opção 2", callback_data='option_2')
    item3 = types.InlineKeyboardButton("Opção 3", callback_data='option_3')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)

# Tratamento das opções do menu embutido
@bot.callback_query_handler(func=lambda call: True)
def handle_inline_menu_options(call):
    if call.data == 'option_1':
        # Lógica para a Opção 1
        bot.send_message(call.message.chat.id, "Você escolheu a Opção 1")
    elif call.data == 'option_2':
        # Lógica para a Opção 2
        bot.send_message(call.message.chat.id, "Você escolheu a Opção 2")
    elif call.data == 'option_3':
        # Lógica para a Opção 3
        bot.send_message(call.message.chat.id, "Você escolheu a Opção 3")

def main():
    # Verificar se todas as variáveis de ambiente necessárias estão definidas
    if not TELEGRAM_BOT_TOKEN:
        logging.error("Certifique-se de definir a variável de ambiente TELEGRAM_BOT_TOKEN no arquivo .env")
        return

    # Iniciar o bot
    bot.polling()

if __name__ == '__main__':
    main()
