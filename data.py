import pandas as pd
import networkx as nx
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

def Create_Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    dist/=1000
    G = nx.DiGraph()
    for st in bicing.itertuples():
        coord1 = (st.lat, st.lon)
        G.add_node(coord1)
        for dt in bicing.itertuples():
            coord2 = (dt.lat, dt.lon)
            if(coord1 != coord2 and haversine(coord1, coord2) <= dist):
                G.add_edge(coord1, coord2)
    print(list(G.edges))
    return G




def main():
    G = Create_Graph(1)

    #geolocator = Nominatim(user_agent="bicing_bot")
    #location1 = geolocator.geocode('Jordi Girona, Barcelona')
    #print(location1.latitude)
main()
