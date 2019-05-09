import pep8
import pandas as pd
import networkx as nx
import staticmap as stm
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

def Create_Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    G = nx.Graph()
    n = bicing.size
    for st in bicing.itertuples():
        coord1 = (st.lon, st.lat)
        G.add_node(coord1)
        for dt in bicing.itertuples():
            coord2 = (dt.lon, dt.lat)
            if(st != dt and haversine(coord1, coord2) <= dist):
                G.add_edge(coord1, coord2)

    return G

def Paint_Graph(G):
    try:
        m_bcn = stm.StaticMap(1500, 1500)
        for node in G.nodes:
            marker = stm.CircleMarker((node[0], node[1]) , 'red', 3 )#esto es el tamaño del punto
            m_bcn.add_marker(marker)

        for edge in G.edges:
            linea = stm.Line((edge[0],edge[1]), 'blue', 1)
            m_bcn.add_line(linea)

        image = m_bcn.render()
        image.save('estaciones.png')
    except:
        print("This is not a graph!")

def main():
    x=read(int)
    G = Create_Graph(x)
    print(G.number_of_nodes())
    print(list(G.edges))
    Paint_Graph(G)


    #geolocator = Nominatim(user_agent="bicing_bot")
    #location1 = geolocator.geocode('Salvador Espriu, Mollet del Valles')
    #location2 = geolocator.geocode('Mar, Orihuela')
    #coord1 = (location1.latitude, location1.longitude)
    #coord2 = (location2.latitude, location2.longitude)
    #print(haversine(coord1, coord2))
main()
