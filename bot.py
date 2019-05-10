import telegram
#import data.py as data
from telegram.ext import Updater
from telegram.ext import CommandHandler

def start(bot, update):
    print(bot)
    print(update)
    botname = bot.username
    username = update.message.chat.username
    fullname = update.message.chat.first_name + ' ' + update.message.chat.last_name
    missatge = "Tu ets en %s (%s) i jo soc el %s." % (fullname, username, botname)
    bot.send_message(chat_id=update.message.chat_id, text=missatge)


TOKEN = open('token.txt').read().strip()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))

updater.start_polling()
