import telegram
import os
import data as d
import set as set
import networkx as nx
from geopy.geocoders import Nominatim
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater


'''
The start function is the firt command the user must call when
using the bot. It creates a graph with size 1km and welcomes the user.
'''
def start(bot, update, user_data):
    G = d.Graph()
    user_data['graph'] = G
    username = update.message.chat.first_name
    bot.send_message(chat_id=update.message.chat_id, text="Hi, %s.\nMy mission is to help you to move throughout Barcelona by bicing. Remember, if you're lost just ask for -> /help.😄😄\n" % username)


'''
Prints the name of the author of this code.
'''
def authors(bot, update):
    message = "Made by: \n" \
              "Àlex Ferrando de las Morenas \n" \
              "& \n" \
              "Elías Abad Rocamora \n" \
              "___________________________________________\n" \
              "Universitat Politècnica de Catalunya, 2019"
    bot.send_message(chat_id=update.message.chat_id, text=message)


'''
This command creates a graph of the given distance given.
'''
def graph(bot, update, args, user_data):
    if len(args) == 1:
        if int(args[0]) < 0:
            bot.send_message(chat_id=update.message.chat_id, text="Please, enter a positive distance")
        else:
            G = d.Graph(int(args[0]))
            user_data['graph'] = G
            bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: %s" % args[0])
    elif len(args) == 0:  # if no distance is provided, it creates a graph with distance 1000.
        G = d.Graph()
        user_data['graph'] = G
        bot.send_message(chat_id=update.message.chat_id, text="Graph created with distance: 1000")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="You should only introduce one distance")


'''
Plots the graph onto the Barcelona map considering nodes are their respective
bicing station.
'''
def plotgraph(bot, update, user_data):
    id = str(update.message.chat_id)
    message_load = bot.send_message(chat_id=update.message.chat_id, text="Processing the map...🕗🕘🕙")
    filename = 'plotgraph' + '_' + id + '.png'
    d.Plotgraph(user_data['graph'], filename)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(filename, 'rb'))
    bot.delete_message(message_load.chat_id, message_load.message_id)
    os.remove(filename)


'''
Prints the nodes' graph number.
'''
def nodes(bot, update, user_data):
    nodes = d.Nodes(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d nodes" % nodes)


'''
Prints the edges' graph number.
'''
def edges(bot, update, user_data):
    edges = d.Edges(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d edges" % edges)


'''
Prints the number of connected components of the graph.
'''
def components(bot, update, user_data):
    components = d.Components(user_data['graph'])
    bot.send_message(chat_id=update.message.chat_id, text="This Graph has: %d connected components" % components)


'''
This function transforms the arguments from a user's message to a string and
returns it.
'''
def args_in_a_line(args):
    sentence = ''
    for arg in args:
        sentence += str(arg) + ' '
    return sentence


'''
Given a tuple with 3 numbers, returns a string with time format.
'''
def output_time(time):
    message = 'Time from start to destination: '
    if time[0] != 0:
        message += "%d h " % time[0]
    if time[0] != 0 or time[1] != 0:
        message += "%d m " % time[1]
    message += "%d s" % time[2]
    return message


''' *************************** Route functions *************************** '''
# We have decided to introduce this set of functions in the bot.py code instead
# of writing it in the data.py to treate the user input in a much simpler way
# avoiding a complicated and excessive amount of code.

'''
If the user provides only one address this function tries to return user's
current coordinates and final address coordinates. If it's not possible
the appropiate message is printed.
'''
def from_ubi_to_destination(address, update, bot, user_data):
    geolocator = Nominatim(user_agent="bicing_bot")
    try:
        coord = user_data['coords']
    except:  # if user location is not stored ask for it
        bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that your current location is not available. Send it to me and try it again")
    location1 = geolocator.geocode(address + ', Barcelona')
    if location1 == None:
        bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that the direction given doesn't exist. Please try it again.")
    return coord, (location1.latitude, location1.longitude)


'''
Detects if two addresses are given. If it's the case, tries to return initial
and final coordinates. If some of them doesn't exist prints an error.
'''
def addressesTOcoordinates(addresses, update, bot, user_data):
    geolocator = Nominatim(user_agent="bicing_bot")
    try:
        address1, address2 = addresses.split(',')
    except:
        return from_ubi_to_destination(addresses, update, bot, user_data)
    try:
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        if(location1 == location2):
            bot.send_message(chat_id=update.message.chat_id, text="Just don't move")
        else:
            return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that some direction doesn't exist. Please try it again.")


'''
As both options route must use the same code this is a unitary code for
both them: fastest_route and route. It sends an image of the route. A green
point indicates the start point, in blue color the paths the user must cycle
and in orange color the paths in which user's must walk. Moreover, it prints
the journey's estimated time.
'''
def do_route(option, bot, update, args, user_data):
    addresses = args_in_a_line(args)
    coord1, coord2 = addressesTOcoordinates(addresses, update, bot, user_data)
    id = str(update.message.chat_id)
    filename = 'shortest_path' + '_' + id + '.png'
    message_load = bot.send_message(chat_id=update.message.chat_id, text="Processing the map...🕗🕘🕙")
    if option:
        time = d.Route1(user_data['graph'], coord1, coord2, filename)
    else:
        time = d.Route2(user_data['graph'], coord1, coord2, filename)
    bot.send_photo(chat_id=update.message.chat_id, photo=open(filename, 'rb'))
    bot.delete_message(message_load.chat_id, message_load.message_id)
    os.remove(filename)
    bot.send_message(chat_id=update.message.chat_id, text=output_time(time))


# Calls the function do route with the option 1.
def route(bot, update, args, user_data): do_route(1, bot, update, args, user_data)


# Calls the function do route with the option 0.
def fastest_route(bot, update, args, user_data): do_route(0, bot, update, args, user_data)

''' ************************************************************************ '''


'''
Tries to access to the user's current location. If it succeeds, prints a map
with the path, the name of the nearest_station and the estimated time to arrive
to that station.
'''
def nearest_station(bot, update, user_data, args):
    geolocator = Nominatim(user_agent="bicing_bot")
    err = False
    if len(args) != 0:
        try:
            address = args_in_a_line(args)
            location = geolocator.geocode(address + ', Barcelona')
            coord = (location.latitude, location.longitude)
        except:
            bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that the direction given doesn't exist. Please try it again.")
            err = True
    else:
        try:
            coord = user_data['coords']
        except:
            bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Ups! It seems that your current location is not available. Send it to me and try it again")
            err = True
    if not err:
        message_load = bot.send_message(chat_id=update.message.chat_id, text="Processing...🕗🕘🕙")
        id = str(update.message.chat_id)
        filename = 'nearest_station' + '_' + id + '.png'
        n_station, time = d.Nearest_station(user_data['graph'], coord, filename)
        bot.send_message(chat_id=update.message.chat_id, text=n_station)
        id = str(update.message.chat_id)
        bot.send_photo(chat_id=update.message.chat_id, photo=open(filename, 'rb'))
        bot.delete_message(message_load.chat_id, message_load.message_id)
        os.remove(filename)
        time = output_time(time)
        bot.send_message(chat_id=update.message.chat_id, text=time)

'''
Given the current graph we are working with and the number of required bikes and
docks for each station, this algorithm calculates the mimimum cost flow of bikes
between stations in the graph so that these requirements are guaranteed.
'''
def distribute(bot, update, args, user_data):
    argerror = False
    if len(args) != 2 or int(args[0]) < 0 or int(args[1]) < 0 or (int(args[0]) == 0 and int(args[1]) == 0):
        argerror = True
    if argerror:
        bot.send_message(chat_id=update.message.chat_id, text="You have to introduce 2 positive numbers next to the command:\nThe number of bikes and the number of docks\nMorover, one of them must be greater than 0")
    else:
        requiredBikes = int(args[0])
        requiredDocks = int(args[1])
        '''
        If the variable error takes True as a value, the variable
        flowCost will indicate which error happened during the calculus
        of the distribution (1 means that it's imposible to guarantee those
        conditions and 2 means that a fatal error ocurred, which is
        a really bad thing).
        The list steps is a list containing how many bikes should be moved,
        the source and destination stations, but it is not used because of
        the problems with the output.
        '''
        steps, total_cost, biggest_cost, error = d.distribute(user_data['graph'], requiredBikes, requiredDocks)
        if error and total_cost == 1:
            bot.send_message(chat_id=update.message.chat_id, text="There's no possible solution for this conditions")
        elif error and total_cost == 2:
            bot.send_message(chat_id=update.message.chat_id, text="💣💣💣 Fatal Error: Incorrect graph model! 💣💣💣")
        else:
            message = "The total cost of transferring bikes is:\n" + \
                       str((int(total_cost*1000))/1000) + " km.\n" \
                      "The biggest cost move is:\n" + \
                       str(int((biggest_cost[0]*1000))/1000) + " km*bikes, between stations " + str(biggest_cost[1]) + " and " + str(biggest_cost[2])
            bot.send_message(chat_id=update.message.chat_id, text=message)


'''
Prints a help message.
'''
def help(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text="That's what I can do for you:\n\n/start: Starts the bot and creates a graph of distance 1000. \n/graph *<distance>*: I''ll create a graph with the given distance. If you don't specify any distance, I'll do it with distance 1000. \n/route *'<address1>' <address2>*: I'll tell you how to arrive from address1 to address2, navigating through the graph and just cycling once. *Remark:* if you only indicate the final address, I'll display the route from your current location. _Make sure you've send it to me_. 😜 \n/fastest\_route *'<address1>' <address2>*: It's like the route command, but I'll let you cycle more than once in order to show you the real fastest route. 🚀🚀 \n/authors: I'll tell you the authors beyond this masterpiece. 😎 \n/nodes: Prints the node's graph number. \n/edges: Prints the edges' graph number. \n/components: Prints the connected components' graph number. \n/nearest\_station: I'll show you the nearest station to your location. \n/plotgraph: Sends you an image of the graph. \n/help: Sounds methaforical 🤔🤔", parse_mode='Markdown')


'''
Stores the user's location when it's sended.
'''
def location(bot, update, user_data):
    user_data['coords'] = update.message.location.latitude, update.message.location.longitude
    coord = user_data['coords']
    message = set.random_location_message()
    bot.send_message(chat_id=update.message.chat_id, text=message)


'''
This command handles unknown commands. Displays a random gif from the collection
in the set.py file.
'''
def unknown(bot, update):
    animation = set.random_gif()
    bot.send_animation(chat_id=update.message.chat_id, animation=animation)
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command 😅")


''' ************************************************************************ '''

TOKEN = open('token.txt').read().strip()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

''' ******************************* Handlers ******************************* '''

dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))

dispatcher.add_handler(CommandHandler('authors', authors))

dispatcher.add_handler(CommandHandler('graph', graph, pass_args=True, pass_user_data=True))

dispatcher.add_handler(CommandHandler('nodes', nodes, pass_user_data=True))

dispatcher.add_handler(CommandHandler('edges', edges, pass_user_data=True))

dispatcher.add_handler(CommandHandler('components', components, pass_user_data=True))

dispatcher.add_handler(CommandHandler('plotgraph', plotgraph, pass_user_data=True))

dispatcher.add_handler(CommandHandler('route', route, pass_args=True, pass_user_data=True))

dispatcher.add_handler(CommandHandler('fastest_route', fastest_route, pass_args=True, pass_user_data=True))

dispatcher.add_handler(CommandHandler('nearest_station', nearest_station, pass_user_data=True, pass_args=True))

dispatcher.add_handler(CommandHandler('distribute', distribute, pass_args=True, pass_user_data=True))

dispatcher.add_handler(CommandHandler('help', help, pass_user_data=True))

dispatcher.add_handler(MessageHandler(Filters.command, unknown))

dispatcher.add_handler(MessageHandler(Filters.location, location, pass_user_data=True))

updater.start_polling()

''' ************************************************************************ '''
