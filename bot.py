import telegram
import os
import data as d
from telegram.ext import Updater
from geopy.geocoders import Nominatim
from telegram.ext import CommandHandler, MessageHandler, Filters

#Añadido creación de grafo por defecto con dist = 1000
def start(bot, update, user_data):
    G = d.Graph()
    user_data['graph'] = G
    username = update.message.chat.first_name
    bot.send_message(chat_id=update.message.chat_id, text="Hi, %s.\nWhat can I do for you?" % username)

#que fino willy
def PutosCracks(bot, update):
    message = "Made by: \n" \
              "Àlex Ferrando de las Morenas \n" \
              "& \n" \
              "Elías Abad Rocamora \n" \
              "___________________________________________\n" \
              "Universitat Politècnica de Catalunya, 2019"
    bot.send_message(chat_id=update.message.chat_id, text = message)

def graph(bot, update, args, user_data):
    if len(args) == 1:
        G = d.Graph(int(args[0]))
        user_data['graph'] = G
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: %s" % args[0])
    elif len(args) == 0:
        G = d.Graph()
        user_data['graph'] = G
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: 1000")
    else: bot.send_message(chat_id=update.message.chat_id, text="You should only introduce one distance")

#d.Plotgraph crea una imagen con nombre filename, se manda esta imagen
#por chat y se elimina del directorio
def plotgraph(bot, update, user_data):
    id = str(update.message.chat_id)
    filename = 'stations' + '_' + id + '.png'
    #este mensaje es solo pa ver lo chulo que queda el nombre del archivo
    bot.send_message(chat_id=update.message.chat_id, text = filename)
    # te molaria poner aqui un mensaje del tipo que espere un momento,
    # porque tarda un poco y eso. si no suda tampoco es nada importante
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

def from_ubi_to_coordinates(address, update, bot, user_data):
    geolocator = Nominatim(user_agent = "bicing_bot")
    try : coord = user_data['coords']
    except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that your current location is not available. Send it to me and try it again")
    try:location1 = geolocator.geocode(address + ', Barcelona')
    except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that the direction given doesn't exist. Please try it again.")
    return (location1.latitude, location1.longitude), coord


def addressesTOcoordinates(addresses, update, bot, user_data):
    geolocator = Nominatim(user_agent = "bicing_bot")
    try: address1, address2 = addresses.split(',')
    #entra al except si no hay una coma en el mensaje, es decir, solo hay una dirección
    except: return from_ubi_to_coordinates(addresses, update, bot, user_data)
    try:
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that some direction doesn't exist. Please try it again.")

def route(bot, update, args, user_data):
    addresses = args_in_a_line(args)
    coord1, coord2 = addressesTOcoordinates(addresses, update, bot, user_data)
    id = str(update.message.chat_id)
    filename = 'shortest_path' + '_' + id + '.png'
    time = d.Route(user_data['graph'], coord1, coord2, filename)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    os.remove(filename)
    message = time_output(time)
    bot.send_message(chat_id=update.message.chat_id, text = message)

def where(bot, update, user_data):
    user_data['coords'] = update.message.location.latitude, update.message.location.longitude
    coord = user_data['coords']
    print(coord)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command 😅")

TOKEN = open('token.txt').read().strip()

updater = Updater(token = TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start, pass_user_data = True))

dispatcher.add_handler(CommandHandler('authors', PutosCracks))

dispatcher.add_handler(CommandHandler('graph', graph, pass_args = True, pass_user_data = True))

dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data = True))

dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data = True))

dispatcher.add_handler(CommandHandler('components', components, pass_user_data = True))

dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_user_data = True))

dispatcher.add_handler(CommandHandler('route', route, pass_args = True, pass_user_data = True))

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

dispatcher.add_handler(MessageHandler(Filters.location, where, pass_user_data=True))

updater.start_polling()
