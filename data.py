import pep8
import pandas as pd
import networkx as nx
import staticmap as stm
import collections as cl
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read, read_line

Pandas = cl.namedtuple('Pandas', 'lat lon')

def Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    G = nx.Graph()
    for st in bicing.itertuples():
        coord1 = (st.lat, st.lon)
        G.add_node(st)
        for dt in bicing.itertuples():
            coord2 = (dt.lat, dt.lon)
            if(st != dt and haversine(coord1, coord2) <= dist): G.add_edge(st, dt)
    print("Graph created!")
    return G

def Plotgraph(G,name):
    try:
        m_bcn = stm.StaticMap(1000, 1000)
        for node in G.nodes:
            marker = stm.CircleMarker((node.lon, node.lat) , 'red', 3 )#esto es el tamaño del punto
            m_bcn.add_marker(marker)

        for edge in G.edges:
            line = stm.Line(((edge[0].lon, edge[0].lat),(edge[1].lon, edge[1].lat)), 'blue', 0)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save(name)
        print("Image done!")
    except:
        print("This is not a graph!") # Revisar en el futuro el try / excepts

def Components(G):
    print("This Graph has", G.number_connected_components(), "connected components")

def Nodes(G):
    print("This Graph has", G.number_of_nodes(), "nodes")

def Edges(G):
    print("This Graph has", G.number_of_edges(), "edges")

def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent = "bicing_bot")
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None

def Route(G, addresses):
    coord1, coord2 = addressesTOcoordinates(addresses)
    print(coord1)
    print(coord2)
    Gc = nx.complement(G)
    #este bucle modifica los pesos
    for edge in Gc.edges:
        weight=haversine((edge[0].lat, edge[0].lon), (edge[1].lat, edge[1].lon))
        Gc.add_edge(edge[0],edge[1],weight = 10/4*weight)
    '''
    ATENCION, para añadir los nodes coord1 y coord2,
    los he creado de manera que se pueda acceder a sus coordenadas de la forma:
    noseque.lat noseque.lon, para eso he creao un tipo namedtuple, que es lo mismo
    que te devuelve itertuples() y por lo tanto el mismo formato que tienen las
    estaciones del DataFrame.
    '''
    start = Pandas(lat=coord1[0] , lon=coord1[1])
    finish = Pandas(lat=coord2[0] , lon=coord2[1])
    Gc.add_node(start)
    Gc.add_node(finish)
    #este añade las arestas que unen start y finish con los demás
    for node in Gc.nodes:
        weight1=haversine((node.lat, node.lon),(start.lat, start.lon))
        weight2=haversine((node.lat, node.lon),(finish.lat, finish.lon))
        Gc.add_edge(node,start,weight = 10/4*weight1)
        Gc.add_edge(node,finish,weight = 10/4*weight2)
    Plotgraph(Gc,'complement.png')
    Gc = nx.compose(G, Gc)
    Plotgraph(Gc,'union.png')
    print(nx.dijkstra_path(Gc,start,finish))

    # hacer dykstra con Gc
    # ¿Crear un nuevo grafo con el trayecto dado para poder printearlo?
    # Se podría calcular el tiempo estimado que tardará en hacer el trayecto.

def main():
    print("Introduce graph's distance: ", end = '')
    G = Graph(read(int))
    action = read(str)
    while action is not None:
        if action == "graph":
            G = Graph(read(int))
        elif action == "plotgraph": Plotgraph(G,'stations.png')
        elif action == "components": Components(G)
        elif action == "nodes": Nodes(G)
        elif action == "edges": Edges(G)
        elif action == "route":
            addresses = read_line()
            Route(G, addresses)
        action = read(str)
main()
