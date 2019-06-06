import time
import pandas as pd
import networkx as nx
import staticmap as stm
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from haversine import haversine
import collections as cl
from jutge import read, read_line

url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')


def Sorting_algorithm(dist=1000):
    G = nx.Graph()
    v = sorted(list(bicing.itertuples()), key=lambda station: station.lat)
    for i in range(len(v)):
        G.add_node(v[i])
        j = i + 1
        while(j < len(v) and v[j].lat - v[i].lat <= dist):
            distance = haversine((v[i].lat, v[i].lon), (v[j].lat, v[j].lon))
            if distance <= dist:
                G.add_edge(v[i], v[j], weight = distance)
            j += 1
    return G


def Create_Matrix(bicing, dist, sizex, sizey, lat_min, lon_min):
    matrix = [[list() for j in range(sizey)] for i in range(sizex)]
    for st in bicing.itertuples():
        dpx = int(haversine((lat_min, st.lon), (st.lat, st.lon)) // dist)
        dpy = int(haversine((st.lat, lon_min), (st.lat, st.lon)) // dist)
        matrix[dpx][dpy].append(st)

    return matrix


def possible_quadrants(M, i, j, verticales, horizontales):
    pos = [(M[i][j])]
    if i + 1 < verticales:
        pos.append(M[i + 1][j])
        if j + 1 < horizontales:
            pos.append(M[i + 1][j + 1])
    if j + 1 < horizontales:
        pos.append(M[i][j+1])
        if i - 1 >= 0:
            pos.append(M[i - 1][j + 1])
    return pos


def Graph_creation(M, dist):
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
                        if distance <= dist and point != point2:
                            G.add_edge(point, point2, weight=distance)
    return G


def Create_Graph(bicing, dist, sizex, sizey, lat_min, lon_min):
    M = Create_Matrix(bicing, dist, sizex, sizey, lat_min, lon_min)
    return Graph_creation(M, dist)


def Calculate_dimensions(bicing, dist):
    first = True
    for st in bicing.itertuples():
        if first:
            lat_min = lat_max = st.lat
            lon_min = lon_max = st.lon
            first = False
        else:
            if st.lat < lat_min:
                lat_min = st.lat
            elif st.lat > lat_max:
                lat_max = st.lat
            if st.lon < lon_min:
                lon_min = st.lon
            elif st.lon > lon_max:
                lon_max = st.lon
    sizex = int(haversine((lat_min, lon_min), (lat_max, lon_min)) // dist + 1)
    sizey = int(haversine((lat_min, lon_min), (lat_min, lon_max)) // dist + 1)
    return sizex, sizey, lat_min, lon_min


def Linear_Graph(dist=1000):
    dist /= 1000
    sizex, sizey, lat_min, lon_min = Calculate_dimensions(bicing, dist)
    return Create_Graph(bicing, dist, sizex, sizey, lat_min, lon_min)

def Quadratic_graph(dist=1000):
    G = nx.Graph()
    dist /= 1000
    for st in bicing.itertuples():
        G.add_node(st)
        for dt in bicing.itertuples():
            distancia = haversine((st.lat, st.lon), (dt.lat, dt.lon))
            if st != dt and dist <= distancia:
                G.add_edge(st, dt, weight=distancia)


def read_input():
    print("Hi, this is an efficiency test to prove the graph creation speed.")
    inicio = 0
    while inicio < 2:
        print("Please, introduce an start distance for the loop (bigger than 2): ")
        inicio = read(int)
    fin = inicio
    while fin <= inicio:
        print("Fine, now introduce a finish distance for the loop (bigger than the start distance)")
        fin = read(int)
    incremento = 0
    while incremento <= 0:
        print("Finally, introduce an increment for the loop (bigger than 0):")
        incremento = read(int)
    return inicio, fin, incremento


def main():
    inicio, fin, incremento = read_input()
    vx = []
    v1 = []
    v2 = []
    v3 = []
    for i in range(inicio, fin, incremento):
        vx.append(i)

    for x in range(inicio, fin, incremento):
        c = 0
        r = 0
        sr = 0
        cont = 0
        cont += 1

        start1 = time.time()
        G = Quadratic_graph(x)
        finish1 = time.time()
        c += finish1 - start1
        print("Quadratic done")

        start2 = time.time()
        Gp = Sorting_algorithm(x)
        finish2 = time.time()
        r += finish2 - start2
        print("Medium speed done")

        start3 = time.time()
        Gq = Linear_Graph(x)
        finish3 = time.time()
        sr += finish3 - start3
        print("Linear done")

        print("This has been with distance ==", x)
        v1.append(c / cont)
        v2.append(r / cont)
        v3.append(sr / cont)

    plt.plot(vx, v1, 'ro')
    plt.plot(vx, v2, 'bs')
    plt.plot(vx, v3, 'g^')
    plt.axis([inicio, fin, 0, 2])
    plt.show()
main()
