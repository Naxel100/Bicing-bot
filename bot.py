import telegram
import os
import data as d
import gif as gif
import networkx as nx
from telegram.ext import Updater
from geopy.geocoders import Nominatim
from telegram.ext import CommandHandler, MessageHandler, Filters

def start(bot, update, user_data):
    print("puta")
    G = d.Graph_supremo_nivel_9000()
    print("hola")
    user_data['graph'] = G
    username = update.message.chat.first_name
    bot.send_message(chat_id=update.message.chat_id, text="Hi, %s.\nWhat can I do for you?" % username)


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
        G = d.Graph_supremo_nivel_9000(int(args[0]))
        print("hola")
        user_data['graph'] = G
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: %s" % args[0])
    elif len(args) == 0:
        G = d.Graph_supremo_nivel_9000()
        user_data['graph'] = G
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: 1000")
    else: bot.send_message(chat_id=update.message.chat_id, text="You should only introduce one distance")



def plotgraph(bot, update, user_data):
    id = str(update.message.chat_id)
    message_load = bot.send_message(chat_id=update.message.chat_id, text = "Processing the map...🕗🕘🕙")
    filename = 'plotgraph' + '_' + id + '.png'
    d.Plotgraph(user_data['graph'] , filename)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    bot.delete_message(message_load.chat_id, message_load.message_id)
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


def args_in_a_line(args):
    direction = ''
    for arg in args:
        direction += str(arg) + ' '
    return direction


def output_time(time):
    message = 'Time from start to destination: '
    if time[0] != 0: message += "%d h " % time[0]
    if time[0] != 0 or time[1] != 0: message += "%d m " % time[1]
    message += "%d s" % time[2]
    return message


def from_ubi_to_destination(address, update, bot, user_data):
    geolocator = Nominatim(user_agent = "bicing_bot")
    try : coord = user_data['coords']
    except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that your current location is not available. Send it to me and try it again")
    try: location1 = geolocator.geocode(address + ', Barcelona')
    except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that the direction given doesn't exist. Please try it again.")
    return (location1.latitude, location1.longitude), coord


def addressesTOcoordinates(addresses, update, bot, user_data):
    geolocator = Nominatim(user_agent = "bicing_bot")
    try: address1, address2 = addresses.split(',')
    except: return from_ubi_to_destination(addresses, update, bot, user_data)
    try:
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        if(location1 == location2): bot.send_message(chat_id=update.message.chat_id, text="Just don't move")
        else: return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that some direction doesn't exist. Please try it again.")


def do_route(option, bot, update, args, user_data):
    print(option)
    addresses = args_in_a_line(args)
    coord1, coord2 = addressesTOcoordinates(addresses, update, bot, user_data)
    id = str(update.message.chat_id)
    filename = 'shortest_path' + '_' + id + '.png'
    message_load = bot.send_message(chat_id=update.message.chat_id, text = "Processing the map...🕗🕘🕙")
    if option: time = d.Route1(user_data['graph'], coord1, coord2, filename)
    else: time = d.Route2(user_data['graph'], coord1, coord2, filename)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    bot.delete_message(message_load.chat_id, message_load.message_id)
    os.remove(filename)
    bot.send_message(chat_id=update.message.chat_id, text = output_time(time))


def route(bot, update, args, user_data): do_route(1, bot, update, args, user_data)


def fastest_route(bot, update, args, user_data): do_route(0, bot, update, args, user_data)


def nearest_station(bot, update, user_data, args):
    geolocator = Nominatim(user_agent = "bicing_bot")
    try:
        address = args_in_a_line(args)
        location = geolocator.geocode(address + ', Barcelona')
        coord = (location.latitude, location.longitude)
    except:
        try : coord = user_data['coords']
        except: bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that your current location is not available. Send it to me and try it again")
    message_load = bot.send_message(chat_id=update.message.chat_id, text = "Processing...🕗🕘🕙")
    id = str(update.message.chat_id)
    filename = 'nearest_station' + '_' + id + '.png'
    n_station, time = d.Nearest_station(user_data['graph'], coord, filename)
    bot.send_message(chat_id=update.message.chat_id, text = n_station)
    id = str(update.message.chat_id)
    bot.send_photo(chat_id=update.message.chat_id, photo = open(filename, 'rb'))
    bot.delete_message(message_load.chat_id, message_load.message_id)
    os.remove(filename)
    time = output_time(time)
    bot.send_message(chat_id=update.message.chat_id, text = time)


def location(bot, update, user_data):
    user_data['coords'] = update.message.location.latitude, update.message.location.longitude
    coord = user_data['coords']
    print(coord)

def unknown(bot, update):
    animation = gif.random_gif()
    bot.send_animation(chat_id=update.message.chat_id, animation = animation)
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

dispatcher.add_handler(CommandHandler('fastest_route', fastest_route, pass_args = True, pass_user_data = True))

dispatcher.add_handler(CommandHandler('nearest_station', nearest_station, pass_user_data = True, pass_args = True))

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

dispatcher.add_handler(MessageHandler(Filters.location, location, pass_user_data=True))

updater.start_polling()
