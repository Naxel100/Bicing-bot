import telegram
import data as d
from telegram.ext import Updater
from telegram.ext import CommandHandler

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hola! Soc un bot bàsic.")

def graph(bot, update, args, user_data):
    try:
        G = d.Graph(int(args[0]))
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: %s" % args[0])
    except:
        G = d.Graph()
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: 1000")
    user_data['graph'] = G

def nodes(bot, update, user_data):
    nodes = d.Nodes(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="%d" % nodes)

def edges(bot, update, user_data):
    edges = d.Edges(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="%d" % edges)

def components(bot, update, user_data):
    components = d.Components(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="%d" % components)

TOKEN = open('token.txt').read().strip()

updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(CommandHandler('graph', graph, pass_args = True, pass_user_data = True))

dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data = True))

dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data = True))

dispatcher.add_handler(CommandHandler('components', components, pass_user_data = True))


dispatcher.add_handler(CommandHandler('plotgraph', plotgraph))

updater.start_polling()
