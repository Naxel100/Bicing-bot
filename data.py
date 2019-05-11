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
            distance = haversine((st.lat, st.lon), (dt.lat, dt.lon))
            if(st != dt and distance <= dist): G.add_edge(st, dt, weight = distance)
    print("Graph created!")              # Chivato
    return G


def Plotgraph(G, filename):
    m_bcn = stm.StaticMap(1000, 1000)

    for node in G.nodes:
        marker = stm.CircleMarker((node.lon, node.lat) , 'red', 3) #esto es el tamaño del punto
        m_bcn.add_marker(marker)

    for edge in G.edges:
        line = stm.Line(((edge[0].lon, edge[0].lat),(edge[1].lon, edge[1].lat)), 'blue', 1)
        m_bcn.add_line(line)

    print("Image done!")                      #Chivato
    image = m_bcn.render()
    image.save(filename)


def time_complete(t):
    h = int(t)
    d = (t - h) * 60
    m = int(d)
    s = int((d - m) * 60)
    return (h, m, s)


def Components(G):
    return nx.number_connected_components(G)


def Nodes(G):
    return nx.number_of_nodes(G)


def Edges(G):
    return nx.number_of_edges(G)

def Plotpath_and_calculate_time(Gc, Path, filename):
        m_bcn = stm.StaticMap(1000, 1000)
        time = 0
        for i in range(len(Path) - 1):
            node1 = Path[i]
            node2 = Path[i + 1]
            distance = haversine((node1.lat, node1.lon), (node2.lat, node2.lon))
            if Gc[node1][node2]['weight'] == distance:
                time += distance / 10
                line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'blue', 2)
            else:
                time += distance / 4
                line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'orange', 2)

            marker1 = stm.CircleMarker((node1.lon, node1.lat) , 'red', 3) #esto es el tamaño del punto
            marker2 = stm.CircleMarker((node2.lon, node2.lat) , 'red', 3) #esto es el tamaño del punto
            m_bcn.add_marker(marker1)
            m_bcn.add_marker(marker2)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save(filename)
        print("Image doneee!")                                # Chivato
        print(time_complete(time))
        return time_complete(time)

def Route(G, coord1, coord2, filename):
    start = Pandas(lat = coord1[0] , lon = coord1[1])
    finish = Pandas(lat = coord2[0] , lon = coord2[1])
    G.add_nodes_from([start, finish])
    #G.add_node(finish)
    Gc = nx.complement(G)
    G.remove_nodes_from([start, finish])
    #G.remove_node(finish)

    #este bucle modifica los pesos
    for edge in Gc.edges:
        distance = haversine((edge[0].lat, edge[0].lon), (edge[1].lat, edge[1].lon))
        Gc.add_edge(edge[0], edge[1], weight = 10/4 * distance)

    Gc = nx.compose(G, Gc)
    Shortest_Path = nx.dijkstra_path(Gc, start, finish)
    return Plotpath_and_calculate_time(Gc, Shortest_Path, filename)

'''
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
'''
