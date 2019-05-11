import pep8
import time
import pandas as pd
import networkx as nx
import staticmap as stm
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read, read_line

def Graph_supuestamente_rapido(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    G = nx.Graph()
    v = sorted(list(bicing.itertuples()), key=lambda station: station.lat)
    for i in range(len(v)):
        G.add_node(v[i])
        j = i + 1
        while(j < len(v) and v[j].lat - v[i].lat <= dist):
            if haversine((v[i].lat, v[i].lon), (v[j].lat, v[j].lon)) <= dist:
                G.add_edge(v[i] , v[j])
            j += 1
    print("Graph done!")
    return G

def Graph_cuadra(dist = 1000):
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



def Components(G):
    print("This Graph has", nx.number_connected_components(G),"connected components")

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

def main():
    x=read(int)
    start1 = time.time()
    G = Graph_cuadra(x)
    finish1 = time.time()
    print("el cuadratico tarda:",finish1 - start1)
    start2 = time.time()
    Gp = Graph_supuestamente_rapido(x)
    finish2 = time.time()
    print("el rapidito tarda:",finish2 - start2)
    Plotgraph(G,'cuadra.png')
    Plotgraph(Gp,'rapidito.png')
    #geolocator = Nominatim(user_agent="bicing_bot")
    #location1 = geolocator.geocode('Salvador Espriu, Mollet del Valles')
    #location2 = geolocator.geocode('Mar, Orihuela')
    #coord1 = (location1.latitude, location1.longitude)
    #coord2 = (location2.latitude, location2.longitude)
    #print(haversine(coord1, coord2))
main()
