import telegram
import data.py as data
from telegram.ext import Updater
from telegram.ext import CommandHandler


TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hola! Soc un bot bàsic.")

dispatcher.add_handler(CommandHandler('start', start))

updater.start_polling()
