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
        G.add_node(coord1)
        for dt in bicing.itertuples():
            coord2 = (dt.lat, dt.lon)
            if(st != dt and haversine(coord1, coord2) <= dist): G.add_edge(coord1, coord2)
    return G

def Plotgraph(G):
    try:
        m_bcn = stm.StaticMap(1000, 1000)
        for node in G.nodes:
            marker = stm.CircleMarker((node[1], node[0]) , 'red', 3 )#esto es el tamaño del punto
            m_bcn.add_marker(marker)

        for edge in G.edges:
            line = stm.Line(((edge[0][1],edge[0][0]),(edge[1][1],edge[1][0])), 'blue', 0)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save('stations.png')
        print("Image done!")
    except:
        print("This is not a graph!") # Revisar en el futuro el try / excepts

def main():
    print("Introduce graph's distance: ", end = '')
    x = read(int)
    G = Graph(x)
    action = read(str)
    while action is not None:
        if action == "graph":
            x = read(int)
            G = Graph(x)
        elif action == "plotgraph": Plotgraph(G)
        elif action == "components": Components(G)
        action = read(str)
main()
