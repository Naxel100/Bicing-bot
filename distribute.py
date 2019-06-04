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
url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
stations = pd.DataFrame.from_records(pd.read_json(url_info)['data']['stations'], index='station_id')
bikes = pd.DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')


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


def distribute(G_bueno, requiredBikes, requiredDocks, radius): # Mirar al final si dist hace falta
    G = nx.DiGraph()
    G.add_node('TOP') # The green node
    demand = 0

    for st in bikes.itertuples():
        idx = st.Index
        stridx = str(idx)

        # The blue (s), black (g) and red (t) nodes of the graph
        a_idx, n_idx, r_idx = 'a'+stridx, 'n'+stridx, 'r'+stridx
        G.add_node(n_idx)
        G.add_node(a_idx)
        G.add_node(r_idx)

        b, d = st.num_bikes_available, st.num_docks_available
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        # Some of the following edges require attributes
        G.add_edge('TOP', a_idx)
        G.add_edge(r_idx, 'TOP')
        G.add_edge(a_idx, n_idx)
        G.add_edge(n_idx, r_idx)

        if req_bikes > 0:
            # NUESTRO
            demandax = req_bikes
            espacios_sobrantes = d - requiredDocks
            if espacios_sobrantes > req_bikes:
                demandax = espacios_sobrantes
            G.nodes[a_idx]['demand'] = -demandax
            G.edges[a_idx,n_idx]['capacity'] = 0
            demand += req_bikes
            # NUESTRO
            # something else must be done here (demand?)
        elif req_docks > 0:
            #NUESTRO
            bicis_sobrantes = b - requiredBikes
            demandax = req_docks
            if bicis_sobrantes > req_docks:
                demandax = bicis_sobrantes
            G.nodes[a_idx]['demand'] = -demandax
            G.edges[r_idx,'TOP']['capacity'] = 0
            #NUESTRO
            demand -= req_docks
            # something else must be done here (demand?)
        '''
        else:
            bicis_disponibles_para_dar = b - requiredBikes
            espacios_disponibles_para_dar = d -requiredDocks
            G.nodes[a_idx]['demand'] = -bicis_disponibles_para_dar
            G.nodes[r_idx]['demand'] = espacios_disponibles_para_dar
            demand += espacios_disponibles_para_dar
            demand -= bicis_disponibles_para_dar
        '''


    G.nodes['TOP']['demand'] = -demand

    for edge in G_bueno.edges():
        #print(edge)
        node1 = edge[0]
        node2 = edge[1]
        id1 = node1.Index
        id2 = node2.Index
        G.add_edge('n'+str(id1), 'n'+str(id2), weight = 1000*G_bueno[node1][node2]['weight'])
        G.add_edge('n'+str(id2), 'n'+str(id1), weight = 1000*G_bueno[node1][node2]['weight'])
    '''
    for idx1, idx2 in it.combinations(stations.index.values, 2):
        coord1 = (stations.at[idx1, 'lat'], stations.at[idx1, 'lon'])
        coord2 = (stations.at[idx2, 'lat'], stations.at[idx2, 'lon'])
        dist = haversine(coord1, coord2)
        if dist <= radius:
            dist = int(dist*1000)
            # The edges must be bidirectional: g_idx1 <--> g_idx2
            G.add_edge('n'+str(idx1), 'n'+str(idx2), weight=dist)
            G.add_edge('n'+str(idx2), 'n'+str(idx1), weight=dist)
    '''
    print('Graph with', G.number_of_nodes(), "nodes and", G.number_of_edges(), "edges.")
    err = False
    sum = 0
    cont = 0
    for node in G.nodes():
        try: sum += G.nodes[node]['demand']
        except: sum = sum
    print(sum)

    try:
        flowCost, flowDict = nx.network_simplex(G)

    except nx.NetworkXUnfeasible:
        err = True
        print("No solution could be found")

    except:
        err = True
        print("***************************************")
        print("*** Fatal error: Incorrect graph model ")
        print("***************************************")

    if not err:
        print("The total cost of transferring bikes is", flowCost/1000, "km.")
        # We update the status of the stations according to the calculated transportation of bicycles
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


def distribute_cortadella(G_bueno, requiredBikes, requiredDocks):
    G = nx.DiGraph()
    G.add_node('TOP') # The green node
    demand = 0

    for st in G_bueno.nodes():
        idx = G_bueno.nodes[st]['Index']


        # The blue (s), black (g) and red (t) nodes of the graph
        a_idx, n_idx, r_idx = 'a'+idx, 'n'+idx, 'r'+idx
        G.add_node(n_idx)
        G.add_node(a_idx)
        G.add_node(r_idx)

        b, d = G_bueno.nodes[st]['bikes'] , G_bueno.nodes[st]['docks']
        req_bikes = max(0, requiredBikes - b)
        req_docks = max(0, requiredDocks - d)

        # Some of the following edges require attributes
        G.add_edge('TOP', a_idx)
        G.add_edge(r_idx, 'TOP')
        G.add_edge(a_idx, n_idx)
        G.add_edge(n_idx, r_idx)

        if req_bikes > 0:
            # NUESTRO
            demandax = req_bikes

            espacios_sobrantes = d - requiredDocks
            if espacios_sobrantes > req_bikes:
                demandax = espacios_sobrantes

            G.nodes[r_idx]['demand'] = demandax
            demand += demandax
            # NUESTRO
            # something else must be done here (demand?)
        elif req_docks > 0:
            #NUESTRO
            demandax = req_docks

            bicis_sobrantes = b - requiredBikes
            if bicis_sobrantes > req_docks:
                demandax = bicis_sobrantes

            G.nodes[a_idx]['demand'] = -demandax
            #NUESTRO
            demand -= demandax
            # something else must be done here (demand?)

    G.nodes['TOP']['demand'] = -demand

    for edge in G_bueno.edges():
        print(edge)
        node1 = edge[0]
        node2 = edge[1]
        id1 = G_bueno.nodes[node1]['Index']
        id2 = G_bueno.nodes[node2]['Index']
        G.add_edge('n'+id1, 'n'+id2, weight = 1000*G_bueno[node1][node2]['weight'])
        G.add_edge('n'+id2, 'n'+id1, weight = 1000*G_bueno[node1][node2]['weight'])

    print('Graph with', G.number_of_nodes(), "nodes and", G.number_of_edges(), "edges.")
    err = False
    sum = 0
    cont = 0
    for node in G.nodes():
        try: sum += G.nodes[node]['demand']
        except: sum = sum
    print(sum)

    try:
        flowCost, flowDict = nx.network_simplex(G)

    except nx.NetworkXUnfeasible:
        err = True
        print("No solution could be found")

    except:
        err = True
        print("***************************************")
        print("*** Fatal error: Incorrect graph model ")
        print("***************************************")

    if not err:
        print("The total cost of transferring bikes is", flowCost/1000, "km.")
        # We update the status of the stations according to the calculated transportation of bicycles
        print(flowDict)
        for src in flowDict:
            if src[0] == 'n': continue
            idx_src = src[1:]
            for dst, b in flowDict[src].items():
                if dst[0] == 'n' and b > 0:
                    idx_dst = dst[1:]
                    print(idx_src, "->", idx_dst, " ", b, "bikes, distance" ''', G[src][dst]['weight']''')
                    G_bueno.nodes[idx_src]['bikes']-= b
                    G_bueno.nodes[idx_dst]['bikes']+= b
                    G_bueno.nodes[idx_src]['docks']+= b
                    G_bueno.nodes[idx_dst]['docks']-= b

def Grapho_cortadella():
    G = nx.Graph()
    G.add_node('A', Index = 'A', bikes = 7, docks = 3)
    G.add_node('B', Index = 'B', bikes = 2, docks = 5)
    G.add_node('C', Index = 'C', bikes = 7, docks = 3)
    G.add_node('D', Index = 'D', bikes = 3, docks = 5)
    G.add_node('E', Index = 'E', bikes = 2, docks = 8)
    G.add_edge('A','B',weight = 2)
    G.add_edge('A','C',weight = 3)
    G.add_edge('A','D',weight = 4)
    G.add_edge('C','D',weight = 3)
    G.add_edge('C','E',weight = 4)
    G.add_edge('C','B',weight = 3)
    G.add_edge('B','E',weight = 1)
    G.add_edge('D','E',weight = 4)
    return G

def main():
    '''
    dist = read(int)
    G_bueno = Graph(dist)
    print("ok")
    x, y = read(int, int)
    distribute(G_bueno, x, y, dist)
    '''
    G_bueno = Grapho_cortadella()
    print("ok")
    x, y = read(int, int)
    distribute_cortadella(G_bueno, x, y)

main()
