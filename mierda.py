import pep8
import time
import pandas as pd
import networkx as nx
import staticmap as stm
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from haversine import haversine
from jutge import read, read_line

url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')

def Graph_supuestamente_rapido(bicing, dist):
    G = nx.Graph()
    v = sorted(list(bicing.itertuples()), key=lambda station: station.lat)
    for i in range(len(v)):
        G.add_node(v[i])
        j = i + 1
        while(j < len(v) and v[j].lat - v[i].lat <= dist):
            distance = haversine((v[i].lat, v[i].lon), (v[j].lat, v[j].lon))
            if distance <= dist: G.add_edge(v[i] , v[j], weight = distance)
            j += 1
    return G

def crear_matriz(bicing, dist, sizex, sizey, lat_min, lon_min):
    #print(sizex, sizey)
    matrix = [[list() for j in range(sizey)] for i in range(sizex)]
    for st in bicing.itertuples():
        dpx = int(haversine((lat_min, st.lon),(st.lat,st.lon)) // dist)
        dpy = int(haversine((st.lat, lon_min),(st.lat,st.lon)) // dist)
        #print(dpx,dpy)
        matrix[dpx][dpy].append(st)

    return matrix

def possible_quadrants(M, i, j, verticales ,horizontales):
    pos = [(M[i][j])]
    if i + 1 < verticales:
        pos.append(M[i + 1][j])
        if j + 1 < horizontales: pos.append(M[i + 1][j + 1])
    if j + 1 < horizontales:
        pos.append(M[i][j+1])
        if i - 1 >= 0: pos.append(M[i - 1][j + 1])
    return pos


def crear_grafo(M, dist):
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


def Graph_supuestamente_aun_mas_rapidito(bicing, dist, sizex, sizey, lat_min, lon_min):
    M = crear_matriz(bicing, dist, sizex, sizey, lat_min, lon_min)
    return crear_grafo(M, dist)

def Calcula_dimensiones(bicing, dist):
    first = True
    lat_min = 0
    lat_max = 0
    lon_min = 0
    lon_max = 0
    for st in bicing.itertuples():
        if first:
            lat_min = st.lat
            lat_max = st.lat
            lon_min = st.lon
            lon_max = st.lon
            first = False
        else:
            if st.lat < lat_min: lat_min = st.lat
            elif st.lat > lat_max: lat_max = st.lat
            if st.lon < lon_min: lon_min = st.lon
            elif st.lon > lon_max: lon_max = st.lon
    sizex = int(haversine((lat_min, lon_min), (lat_max, lon_min)) // dist + 1)
    sizey = int(haversine((lat_min, lon_min), (lat_min, lon_max)) // dist + 1)
    return sizex, sizey, lat_min, lon_min

def Graph_supremo_nivel_9000(dist = 1000):
    if dist == 0: return Graph_supuestamente_rapido(bicing, dist)
    dist /= 1000
    sizex, sizey, lat_min, lon_min = Calcula_dimensiones(bicing, dist)
    casillas = sizex*sizey
    if casillas > 160000:
        return Graph_supuestamente_rapido(bicing, dist)
    else:
        print("casillas:",casillas, "con dist:", dist)
        return Graph_supuestamente_aun_mas_rapidito(bicing, dist, sizex, sizey, lat_min, lon_min)


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
    vx = []
    for i in range(1, 5000, 20):
        vx.append(i)
    print(vx)

    #v1 = []
    #v2 = []
    v3 = []
    for x in range(1, 5000, 20):
        c = 0
        r = 0
        sr = 0
        cont = 0
        for y in range(2):
            cont += 1
            '''
            start1 = time.time()
            G = Graph_cuadra(x)
            finish1 = time.time()
            c += finish1 - start1
            print("1")
            start2 = time.time()
            Gp = Graph_supuestamente_rapido(x)
            finish2 = time.time()
            r += finish2 - start2
            print("2")
            '''
            start3 = time.time()
            Gq = Graph_supremo_nivel_9000(x)
            finish3 = time.time()
            sr += finish3 - start3
            print("3")
        print("esto ha sio con x ==", x)
        #v1.append(c / cont)
        #v2.append(r / cont)
        v3.append(sr / cont)
    print("Puntos malos:")
    for i in range(1, len(v3)-1):
        dist_actual = v3[i]-v3[i-1]
        if dist_actual > 0.05:
            print(i*20)
    #plt.plot(vx, v1, 'ro')
    #plt.plot(vx, v2, 'bs')
    plt.plot(vx, v3, 'g^')
    plt.axis([0, 5000, 0, 1])
    plt.show()
    '''
    x = read(int)
    start1 = time.time()
    Gp = Graph_supuestamente_rapido(x)
    finish1 = time.time()
    print("OK,",finish1-start1)
    start2 = time.time()
    G = Graph_supuestamente_aun_mas_rapidito(x)
    finish2 = time.time()
    print("OK,",finish2-start2)
    '''
    #Plotgraph(G,'cuadra.png')
    #Plotgraph(Gq,'rapidito.png')
    #geolocator = Nominatim(user_agent="bicing_bot")
    #location1 = geolocator.geocode('Salvador Espriu, Mollet del Valles')
    #location2 = geolocator.geocode('Mar, Orihuela')
    #coord1 = (location1.latitude, location1.longitude)
    #coord2 = (location2.latitude, location2.longitude)
    #print(haversine(coord1, coord2))
main()
