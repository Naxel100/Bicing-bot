import telegram
import data as d
from telegram.ext import Updater
from telegram.ext import CommandHandler

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hola! Soc un bot bàsic.")

def graph(bot, update, args):
    try:
        G = d.Graph(int(args[0]))
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: %s" % args[0])
    except:
        G = d.Graph()
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: 1000")

def plotgraph(bot, update):
    bot.send_photo(chat_id=update.message.chat_id, photo=open("stations.png", 'rb'))

TOKEN = open('token.txt').read().strip()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True))

dispatcher.add_handler(CommandHandler('plotgraph', plotgraph))

updater.start_polling()
