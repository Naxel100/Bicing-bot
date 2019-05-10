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
            weight = haversine((st.lat, st.lon), (dt.lat, dt.lon))
            if(st != dt and weight <= dist): G.add_edge(st, dt, weight = weight)
    print("Graph created!")
    return G


def Plotgraph(G, name):
    try:
        m_bcn = stm.StaticMap(1000, 1000)
        for node in G.nodes:
            marker = stm.CircleMarker((node.lon, node.lat) , 'red', 3 ) #esto es el tamaño del punto
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
    geolocator = Nominatim(user_agent = "bicing_bot")
    address1, address2 = addresses.split(',')
    location1 = geolocator.geocode(address1 + ', Barcelona')
    location2 = geolocator.geocode(address2 + ', Barcelona')
    return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)

def Route(G, addresses):
    coord1, coord2 = addressesTOcoordinates(addresses)
    start = Pandas(lat = coord1[0] , lon = coord1[1])
    finish = Pandas(lat = coord2[0] , lon = coord2[1])
    G.add_node(start)
    G.add_node(finish)
    Gc = nx.complement(G)
    G.remove_node(start)
    G.remove_node(finish)

    #este bucle modifica los pesos
    for edge in Gc.edges:
        weight = haversine((edge[0].lat, edge[0].lon), (edge[1].lat, edge[1].lon))
        Gc.add_edge(edge[0], edge[1], weight = 10/4 * weight)

    Gc = nx.compose(G, Gc)
    Shortest_Path = nx.dijkstra_path(Gc, start, finish)

    m_bcn = stm.StaticMap(1000, 1000)

    for i in range(len(Shortest_Path) - 1):
        node1 = Shortest_Path[i]
        node2 = Shortest_Path[i + 1]
        if Gc[node1][node2]['weight'] == haversine((node1.lat, node1.lon), (node2.lat, node2.lon)):
            line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'blue', 2)
        else:
            line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'orange', 2)

        marker1 = stm.CircleMarker((node1.lon, node1.lat) , 'red', 3 ) #esto es el tamaño del punto
        marker2 = stm.CircleMarker((node2.lon, node2.lat) , 'red', 3 ) #esto es el tamaño del punto
        m_bcn.add_marker(marker1)
        m_bcn.add_marker(marker2)
        m_bcn.add_line(line)

    image = m_bcn.render()
    image.save("Shortest_Path.png")
    print("Image done!")

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
