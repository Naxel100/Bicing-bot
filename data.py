import pep8
import pandas as pd
import networkx as nx
import staticmap as stm
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read, read_line

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

def addressesTOcoordinates(addresses):
    try:
        geolocator = Nominatim(user_agent = "bicing_bot")
        print(addresses)
        address1, address2 = addresses.split(',')
        location1 = geolocator.geocode(address1 + ', Barcelona')
        location2 = geolocator.geocode(address2 + ', Barcelona')
        return (location1.latitude, location1.longitude), (location2.latitude, location2.longitude)
    except:
        return None

def Route(G, addresses):
    coord1, coord2 = addressesTOcoordinates(addresses)
    Gc = G.complement()
    for node in Gc.edges:
        coord_node = (node.lat, node.lon)
        Gc.add_edge(node, coord1, weight = 2*haversine(coord_node, coord1))
        Gc.add_edge(node, coord1, weight = 2*haversine(coord_node, coord2))
    Gc = union(G, Gc)
    # hacer dykstra con Gc
    # ¿Crear un nuevo grafo con el trayecto dado para poder printearlo?
    # Se podría calcular el tiempo estimado que tardará en hacer el trayecto.

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
            addresses = read_line()
            Route(G, addresses)
        action = read(str)
main()
