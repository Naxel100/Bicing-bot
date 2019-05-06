import pandas as pd
import networkx as nx
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read

def main():
    G = nx.DiGraph()
    G.add_edge(1,3)
    print(G.number_of_nodes())
    print(list(G.nodes))


    geolocator = Nominatim(user_agent="bicing_bot")
    location1 = geolocator.geocode('Jordi Girona, Barcelona')
    print(location1.latitude)
main()
