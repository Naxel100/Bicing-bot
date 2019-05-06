import pep8
import pandas as pd
import networkx as nx
from staticmap import StaticMap, CircleMarker
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

def Create_Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    G = nx.DiGraph()
    n = bicing.size
    for st in bicing.itertuples():
        coord1 = (st.lat, st.lon)
        G.add_node(coord1)
        for dt in bicing.itertuples():
            coord2 = (dt.lat, dt.lon)
            if(st != dt and haversine(coord1, coord2) <= dist):
                G.add_edge(coord1, coord2)

    return G

def Paint_Graph(G):
    try:
        m_bcn = StaticMap(600, 600)
        for node in G.nodes:
            print(node) #esto no vale pa na, era pa ver como daba los nodes
            #ojo, aqui hay que poner primero longitud y luego latitud
            marker = CircleMarker((node[1], node[0]) , 'red', 6 #esto es el tamaño del punto)
            m_bcn.add_marker(marker)

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
