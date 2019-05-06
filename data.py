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
    location1 = geolocator.geocode('Salvador Espriu, Mollet del Valles')
    location2 = geolocator.geocode('Provença, Barcelona')
    coord1 = (location1.latitude, location1.longitude)
    coord2 = (location2.latitude, location2.longitude)
    print(haversine(coord1, coord2))
main()
