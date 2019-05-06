import pandas as pd
import networkx as nx
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

def Create_Graph(dist = 1):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    G = nx.DiGraph()
    n = bicing.size
    for st in bicing.itertuples():
        coord1 = (st.lat, st.lon)
        G.add_node(coord1)
        dt = st
        while dt != None:
            coord2 = (dt.lat, dt.lon)
            #print(haversine(coord1, coord2))
            if coord1 != coord2 and haversine(coord1, coord2) <= dist: G.add_edge(coord1, coord2)
            dt = dt + 1
    print(list(G.edges))
    return G


def main():
    G = Create_Graph()
    geolocator = Nominatim(user_agent="bicing_bot")
    location1 = geolocator.geocode('Salvador Espriu, Mollet del Valles')
    location2 = geolocator.geocode('Provença, Barcelona')
    coord1 = (location1.latitude, location1.longitude)
    coord2 = (location2.latitude, location2.longitude)
    print(haversine(coord1, coord2))
main()
