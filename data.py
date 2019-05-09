import pep8
import pandas as pd
import networkx as nx
import staticmap as stm
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

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

def Plotgraph(G):
    try:
        m_bcn = stm.StaticMap(1000, 1000)
        for node in G.nodes:
            marker = stm.CircleMarker((node.lon, node.lat) , 'red', 3 )#esto es el tamaño del punto
            m_bcn.add_marker(marker)

        for edge in G.edges:
            line = stm.Line(((edge[0].lon, edge[0].lat),(edge[1].lon, edge[1].lat)), 'blue', 0)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save('stations.png')
        print("Image done!")
    except:
        print("This is not a graph!") # Revisar en el futuro el try / excepts

def Components(G):
    print("This Graph has", G.number_connected_components(), "connected components")

def Nodes(G):
    print("This Graph has", G.number_of_nodes(), "nodes")

def Edges(G):
    print("This Graph has", G.number_of_edges(), "edges")

def Route

def main():
    print("Introduce graph's distance: ", end = '')
    G = Graph(read(int))
    action = read(str)
    while action is not None:
        if action == "graph":
            G = Graph(read(int))
        elif action == "plotgraph": Plotgraph(G)
        elif action == "components": Components(G)
        elif action == "nodes": Nodes(G)
        elif action == "edges": Edges(G)
        elif action == "route":
            adress1, adress2 = read(str, str)
            Route(G, adress1, adress2)
        action = read(str)
main()
