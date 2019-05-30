import pep8
import pandas as pd
import networkx as nx
import staticmap as stm
import collections as cl
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read, read_line

Pandas = cl.namedtuple('Pandas', 'lat lon')


''' ********************************************** Graph creation ********************************************** '''

def possible_quadrants(M, i, j, verticales ,horizontales):
    pos = [(M[i][j])]
    if i + 1 < verticales:
        pos.append(M[i + 1][j])
        if j + 1 < horizontales: pos.append(M[i + 1][j + 1])
    if j + 1 < horizontales:
        pos.append(M[i][j+1])
        if i - 1 >= 0: pos.append(M[i - 1][j + 1])
    return pos


def Create_Graph(M, dist):
    G = nx.Graph()
    verticales = len(M)
    horizontales = len(M[0])
    for i in range(verticales):
        for j in range(horizontales):
            for point in M[i][j]:
                G.add_node(point)
                for quadrant in possible_quadrants(M, i, j, verticales, horizontales):
                    for point2 in quadrant:
                        distance = haversine((point.lat, point.lon), (point2.lat, point2.lon))
                        if distance <= dist and point != point2: G.add_edge(point, point2, weight = distance)
    return G

<<<<<<< HEAD

def Bounding_box_coordinates(bicing, dist):
    first = True
    for st in bicing.itertuples():
        if first:
=======
def dim(bicing, dist):
    first = True
    print("alexxxx")
    for st in bicing.itertuples():
        if first:
            print("first")
>>>>>>> b3cb8dd419f36dbf776256a9e827eee1399b83df
            lat_min = lat_max = st.lat
            lon_min = lon_max = st.lon
            first = False
        else:
            if st.lat < lat_min: lat_min = st.lat
            elif st.lat > lat_max: lat_max = st.lat
            if st.lon < lon_min: lon_min = st.lon
            elif st.lon > lon_max: lon_max = st.lon
<<<<<<< HEAD
    return lat_min, lat_max, lon_min, lon_max


def Create_matrix(bicing, dist):
    lat_min, lat_max, lon_min, lon_max = Bounding_box_coordinates(bicing, dist)
=======
    print("ii")
>>>>>>> b3cb8dd419f36dbf776256a9e827eee1399b83df
    sizex = int(haversine((lat_min, lon_min), (lat_max, lon_min)) // dist + 1)
    sizey = int(haversine((lat_min, lon_min), (lat_min, lon_max)) // dist + 1)

    matrix = [[list() for j in range(sizey)] for i in range(sizex)]
    for st in bicing.itertuples():
        dpx = int(haversine((lat_min, st.lon),(st.lat,st.lon)) // dist)
        dpy = int(haversine((st.lat, lon_min),(st.lat,st.lon)) // dist)
        matrix[dpx][dpy].append(st)

    return matrix


<<<<<<< HEAD
def Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    dist /= 1000
    if dist == 0:
        G = nx.Graph()
        G.add_nodes_from(bicing.itertuples())
        return G
=======
def Graph_supremo_nivel_9000(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    if dist == 0: return Graph_rapido_para_distacias_cortas(bicing, dist)
    dist /= 1000
    print("hooooo")
    sizex, sizey, lat_min, lon_min = dim(bicing, dist)
    casillas = sizex*sizey
    print(casillas)
    if casillas > 160000:
        return Graph_rapido_para_distacias_cortas(bicing, dist)
>>>>>>> b3cb8dd419f36dbf776256a9e827eee1399b83df
    else:
        M = Create_matrix(bicing, dist)
        return Create_Graph(M, dist)
    return G

''' ******************************************************************************************************** '''

def Plotgraph(G, filename):
    m_bcn = stm.StaticMap(1000, 1000)

    for node in G.nodes:
        marker = stm.CircleMarker((node.lon, node.lat) , 'red', 3) #esto es el tamaño del punto
        m_bcn.add_marker(marker)

    for edge in G.edges:
        line = stm.Line(((edge[0].lon, edge[0].lat),(edge[1].lon, edge[1].lat)), 'blue', 1)
        m_bcn.add_line(line)

    image = m_bcn.render()
    image.save(filename)


def time_complete(t):
    h = int(t)
    d = (t - h) * 60
    m = int(d)
    s = int((d - m) * 60)
    return (h, m, s)


def Components(G):
    return nx.number_connected_components(G)


def Nodes(G):
    return nx.number_of_nodes(G)


def Edges(G):
    return nx.number_of_edges(G)


def Plotpath_and_calculate_time(G, Path, filename):
        m_bcn = stm.StaticMap(1000, 1000)
        time = 0
        for i in range(len(Path) - 1):
            node1, node2 = Path[i], Path[i + 1]
            distance = haversine((node1.lat, node1.lon), (node2.lat, node2.lon))
            if G[node1][node2]['weight'] == distance:
                time += distance / 10
                line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'blue', 2)
            else:
                time += distance / 4
                line = stm.Line(((node1.lon, node1.lat),(node2.lon, node2.lat)), 'orange', 2)

            marker1 = stm.CircleMarker((node1.lon, node1.lat) , 'red', 3) #esto es el tamaño del punto
            marker2 = stm.CircleMarker((node2.lon, node2.lat) , 'red', 3) #esto es el tamaño del punto
            m_bcn.add_marker(marker1)
            m_bcn.add_marker(marker2)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save(filename)
        return time_complete(time)

#Calcula el camino más corto, crea la imagen de la ruta a seguir
#y devuelve un vector de la forma: (horas, minutos, segundos) representando
#el tiempo estimado de realización de la ruta.
def Route2(G, coord1, coord2, filename):
    start = Pandas(lat = coord1[0] , lon = coord1[1])
    finish = Pandas(lat = coord2[0] , lon = coord2[1])
    G.add_nodes_from([start, finish])
    Gc = nx.complement(G)
    G.remove_nodes_from([start, finish])
    for edge in Gc.edges:
        distance = haversine((edge[0].lat, edge[0].lon), (edge[1].lat, edge[1].lon))
        Gc.add_edge(edge[0], edge[1], weight = 10/4 * distance)

    Gc = nx.compose(G, Gc)
    Shortest_Path = nx.dijkstra_path(Gc, start, finish)
    return Plotpath_and_calculate_time(Gc, Shortest_Path, filename)


def Route1(G, coord1, coord2, filename):
    start = Pandas(lat = coord1[0] , lon = coord1[1])
    finish = Pandas(lat = coord2[0] , lon = coord2[1])
    max_dist = haversine((start.lat, start.lon), (finish.lat, finish.lon))
    G.add_nodes_from([start, finish])
    for node in G.nodes:
        distance1 = haversine((start.lat, start.lon), (node.lat, node.lon))
        distance2 = haversine((finish.lat, finish.lon), (node.lat, node.lon))
        if node != start and distance1 <= max_dist: G.add_edge(start, node, weight = 10/4 * distance1)
        if node != finish and distance2 <= max_dist: G.add_edge(finish, node, weight = 10/4 * distance2)
    Shortest_Path = nx.dijkstra_path(G, start, finish)
    time = Plotpath_and_calculate_time(G, Shortest_Path, filename)
    print(time)
    G.remove_nodes_from([start, finish])
    return time


def Find_nearest_station(G, coord):
    first = True
    for node in G.nodes:
        coord1 = (node.lat, node.lon)
        dist = haversine(coord, coord1)
        if first:
            min = dist
            first = False
            res = node
        elif dist < min:
            min = dist
            res = node
    return res;

def Plotgraph_graph_to_nearest(n_station, coord):
    m_bcn = stm.StaticMap(1000, 1000)
    line = stm.Line(((coord[1], coord[0]), (n_station.lon, n_station.lat)), 'orange', 2)
    marker1 = stm.CircleMarker((coord[1], coord[0]) , 'red', 3) #esto es el tamaño del punto
    marker2 = stm.CircleMarker((n_station.lon, n_station.lat) , 'red', 3) #esto es el tamaño del punto
    m_bcn.add_marker(marker1)
    m_bcn.add_marker(marker2)
    m_bcn.add_line(line)
    image = m_bcn.render()
    image.save(filename)

def Nearest_station(G, coord, filename):
    n_station = Find_nearest_station(G, coord);
    Plotgraph_graph_to_nearest(n_station, coord, filename)
    time = time_complete(haversine((coord[0], coord[1]), (n_station.lat, n_station.lon)) / 4)
    return res.address, time

'''
def main():
    print("Introduce graph's distance: ", end = '')
    G = Graph(read(int))
    action = read(str)
    while action is not None:
        if action == "graph":
            G = Graph(read(int))
        elif action == "plotgraph": Plotgraph(G,'stations.png')
        elif action == "components": Components(G)
        elif action == "nodes": Nodes(G)
        elif action == "edges": Edges(G)
        elif action == "route":
            addresses = read_line()
            Route(G, addresses)
        action = read(str)
main()
'''
