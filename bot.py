import telegram
import os
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

#d.Plotgraph crea una imagen con nombre filename, se manda esta imagen
#por chat y se elimina del directorio
def plotgraph(bot, update, user_data):
    id = str(update.message.chat_id)
    filename = 'stations' + '_' + id + '.png'
    #este mensaje es solo pa ver lo chulo que queda el nombre del archivo
    bot.send_message(chat_id=update.message.chat_id, text = filename)
    d.Plotgraph(user_data['graph'] , filename)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    os.remove(filename)

def nodes(bot, update, user_data):
    nodes = d.Nodes(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d nodes" % nodes)

def edges(bot, update, user_data):
    edges = d.Edges(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d edges" % edges)

def components(bot, update, user_data):
    components = d.Components(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d connected components" % components)

#lo mismo que read_line pero mejor (puto jutge y Jordi Petit!)
def args_in_a_line(args):
    direction = ''
    for arg in args:
        direction += str(arg) + ' '
    return direction

def time_output(time):
    message = 'Time from start to destination: '
    if time[0] != 0: message += "%d h " % time[0]
    if time[0] != 0 or time[1] != 0: message += "%d m " % time[1]
    message += "%d s" % time[2]
    return message

def route(bot, update, args, user_data):
    addresses = args_in_a_line(args)
    id = str(update.message.chat_id)
    filename = 'shortest_path' + '_' + id + '.png'
    time = d.Route(user_data['graph'], addresses, filename)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    os.remove(filename)
    message = time_output(time)
    bot.send_message(chat_id=update.message.chat_id, text = message)

TOKEN = open('token.txt').read().strip()

updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(CommandHandler('graph', graph, pass_args = True, pass_user_data = True))

dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data = True))

dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data = True))

dispatcher.add_handler(CommandHandler('components', components, pass_user_data = True))

dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_user_data = True))

dispatcher.add_handler(CommandHandler('route', route, pass_args = True, pass_user_data = True))

updater.start_polling()
