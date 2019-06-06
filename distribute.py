import pep8
import time
import pandas as pd
import itertools as it
import networkx as nx
import staticmap as stm
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from haversine import haversine
import collections as cl
from jutge import read, read_line

url_info = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
stations = pd.DataFrame.from_records(pd.read_json(url_info)['data']['stations'], index='station_id')

def Possible_quadrants(M, i, j, verticales ,horizontales):
    pos = [(M[i][j])]
    if i + 1 < verticales:
        pos.append(M[i + 1][j])
        if j + 1 < horizontales: pos.append(M[i + 1][j + 1])
    if j + 1 < horizontales:
        pos.append(M[i][j+1])
        if i - 1 >= 0: pos.append(M[i - 1][j + 1])
    return pos


def Create_linear_Graph(M, dist):
    G = nx.Graph()
    verticales = len(M)
    horizontales = len(M[0])
    for i in range(verticales):
        for j in range(horizontales):
            for point in M[i][j]:
                G.add_node(point)
                for quadrant in Possible_quadrants(M, i, j, verticales, horizontales):
                    for point2 in quadrant:
                        distance = haversine((point.lat, point.lon), (point2.lat, point2.lon))
                        if distance <= dist and point != point2: G.add_edge(point, point2, weight = distance)
    return G

def Bbox_dimensions(bicing, dist):
    first = True
    for st in bicing.itertuples():
        if first:
            lat_min = lat_max = st.lat
            lon_min = lon_max = st.lon
            first = False
        else:
            if st.lat < lat_min: lat_min = st.lat
            elif st.lat > lat_max: lat_max = st.lat
            if st.lon < lon_min: lon_min = st.lon
            elif st.lon > lon_max: lon_max = st.lon
    sizex = int(haversine((lat_min, lon_min), (lat_max, lon_min)) // dist + 1)
    sizey = int(haversine((lat_min, lon_min), (lat_min, lon_max)) // dist + 1)
    return sizex, sizey, lat_min, lon_min


def Create_matrix(bicing, dist, sizex, sizey, lat_min, lon_min):
    matrix = [[list() for j in range(sizey)] for i in range(sizex)]
    for st in bicing.itertuples():
        dpx = int(haversine((lat_min, st.lon),(st.lat,st.lon)) // dist)
        dpy = int(haversine((st.lat, lon_min),(st.lat,st.lon)) // dist)
        matrix[dpx][dpy].append(st)

    return matrix

def Create_by_sort_Graph(bicing, dist):
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


def Graph(dist = 1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index = 'station_id')
    if dist == 0: return Short_distance_Graph(bicing, dist)
    dist /= 1000
    sizex, sizey, lat_min, lon_min = Bbox_dimensions(bicing, dist)
    if sizex*sizey > 160000 or sizex*sizey < 7: return Create_by_sort_Graph(bicing, dist)
    else:
        M = Create_matrix(bicing, dist, sizex, sizey, lat_min, lon_min)
        return Create_linear_Graph(M, dist)



'''*********************************************************************************************'''
'''*********************************************************************************************'''
'''*********************************************************************************************'''
''' NO PASARRRRRR '''


#Puts all the indexes from the Nodes in the graph G in a list
def index_in_a_list(G):
    list = []
    for node in G.nodes():
        list.append(node.Index)
    return list

def distribute(G_original, requiredBikes, requiredDocks):
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = pd.DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')
    G = nx.DiGraph()
    G.add_node('TOP')
    demand = 0
    estaciones_malas = []
    for st in bikes.itertuples():
        idx = st.Index
        if idx not in index_in_a_list(G_original):
            estaciones_malas.append(idx)                   # Justo aqui abajo habia un continue
        stridx = str(idx)
        # The blue (a), black (n) and red (r) nodes of the graph
        a_idx, n_idx, r_idx = 'a'+stridx, 'n'+stridx, 'r'+stridx
        G.add_node(n_idx)
        G.add_node(a_idx)
        G.add_node(r_idx)

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        G.add_edge('TOP', a_idx)
        G.add_edge(r_idx, 'TOP')
        G.add_edge(a_idx, n_idx)
        G.add_edge(n_idx, r_idx)

        if req_bikes > 0:
            demand += req_bikes
            G.nodes[r_idx]['demand'] = req_bikes
            G.edges[a_idx,n_idx]['capacity'] = 0

        elif req_docks > 0:
            demand -= req_docks
            G.nodes[a_idx]['demand'] = -req_docks
            G.edges[n_idx,r_idx]['capacity'] = 0
    print(estaciones_malas)
    G.nodes['TOP']['demand'] = -demand
    print(-demand)
    #adds the edges from our graph to the directed one
    for edge in G_original.edges():
        node1 = edge[0]
        node2 = edge[1]
        id1 = node1.Index
        id2 = node2.Index
        peso = G_original[node1][node2]['weight']
        G.add_edge('n'+str(id1), 'n'+str(id2), cost = int(1000*peso), weight = peso)
        G.add_edge('n'+str(id2), 'n'+str(id1), cost = int(1000*peso), weight = peso)
    print("nodes added succesfuly")
    err = False

    try:
        flowCost, flowDict = nx.network_simplex(G, weight = 'cost')

    except nx.NetworkXUnfeasible:
        err = True
        return 1, "malo", err
        '''
        "No solution could be found"
        '''
    except:
        err = True
        return 2, "malisimo", err
        '''
        "***************************************"
        "*** Fatal error: Incorrect graph model "
        "***************************************"
        '''
    if not err:
        nbikes = 'num_bikes_available'
        ndocks = 'num_docks_available'
        print("The total cost of transferring bikes is", flowCost/1000, "km.")
        for src in flowDict:
            if src[0] != 'n': continue
            idx_src = int(src[1:])
            for dst, b in flowDict[src].items():
                if dst[0] == 'n' and b > 0:
                    idx_dst = int(dst[1:])
                    print(idx_src, "->", idx_dst, " ", b, "bikes, distance", G.edges[src, dst]['weight'])
                    bikes.at[idx_src, nbikes] -= b
                    bikes.at[idx_dst, nbikes] += b
                    bikes.at[idx_src, ndocks] += b
                    bikes.at[idx_dst, ndocks] -= b

def main():
    dist = read(int)
    G_original = Graph(dist)
    print("ok")
    x, y = read(int, int)
    distribute(G_original, x, y)
    '''
    G_original = Grapho_cortadella()
    print("ok")
    x, y = read(int, int)
    distribute_cortadella(G_original, x, y)
    '''
main()
