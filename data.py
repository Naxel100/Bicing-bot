import pandas as pd
import networkx as nx
import staticmap as stm
import collections as cl
from geopy.geocoders import Nominatim
from haversine import haversine


'''
This namedtuple was made in order to add the start and finish points
to the graph, so when calculating the route and access to these points'
coordinates, it could be done the same way as in the points that were stations.
'''
Pandas = cl.namedtuple('Pandas', 'lat lon')


''' ********************************************** Graph creation ******************************************'''

'''
Given the matrix that contains the points of the graph, the indexes i and j
of the quadrant where a certain point is and the dimensions of the matrix,
this algorithm returns the quadrants which may contain points that are suitable
to make new conections with the point we are analizing.
'''
def Possible_quadrants(M, i, j, rows, columns):
    pos = [(M[i][j])]
    if i + 1 < rows:
        pos.append(M[i + 1][j])
        if j + 1 < columns:
            pos.append(M[i + 1][j + 1])
    if j + 1 < columns:
        pos.append(M[i][j+1])
        if i - 1 >= 0:
            pos.append(M[i - 1][j + 1])
    return pos

'''
Given the matrix that contains the points of the graph and the maximum distance
two stations need to have to be connected, returns the final graph with all the
nodes and edges added.
'''
def Create_linear_Graph(M, dist):
    G = nx.Graph()
    rows = len(M)
    columns = len(M[0])
    for i in range(rows):
        for j in range(columns):
            for point in M[i][j]:
                G.add_node(point)
                for quadrant in Possible_quadrants(M, i, j, rows, columns):
                    for point2 in quadrant:
                        distance = haversine((point.lat, point.lon), (point2.lat, point2.lon))
                        if distance <= dist and point != point2:
                            G.add_edge(point, point2, weight=distance)
    return G


'''
Given the bicing DataFrame containing all the station data and the distance that
defines the graph, calculates and returns the number of rows and columns the
matrix containing the points will have and what are the mimimum latitude
and longitude.
'''
def Bbox_dimensions(bicing, dist):
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


'''
Given the DataFrame containing the stations, the distance that defines the graph
and all the mesures returned by the function above, this algorithm creates
and returns a matrix with sizex*sizey quadrants so that the dimensions of
each quadrant are dist*dist, dividing Barcelona by sections and asociating
each bicing station to aquadrant.
'''
def Create_matrix(bicing, dist, sizex, sizey, lat_min, lon_min):
    matrix = [[list() for j in range(sizey)] for i in range(sizex)]
    for st in bicing.itertuples():
        dpx = int(haversine((lat_min, st.lon), (st.lat, st.lon)) // dist)
        dpy = int(haversine((st.lat, lon_min), (st.lat, st.lon)) // dist)
        matrix[dpx][dpy].append(st)

    return matrix


'''
Given the DataFrame containing the stations, the distance that defines the graph,
this algorithm sorts a list of stations by it's latitude and compares a station
with the following ones (creating or not an edge depending on the distance) and
stops with that station with the difference of latitudes is bigger than "dist"
(this means that no more stations can make a connection with that one).
We really like this algorithm because is fast when "dist" is small or big
(not in the median case) and as it can be seen, it is really easy to
implement and understand.
'''
def Create_by_sort_Graph(bicing, dist):
    G = nx.Graph()
    v = sorted(list(bicing.itertuples()), key=lambda station: station.lat)
    for i in range(len(v)):
        G.add_node(v[i])
        j = i + 1
        while(j < len(v) and v[j].lat - v[i].lat <= dist):
            distance = haversine((v[i].lat, v[i].lon), (v[j].lat, v[j].lon))
            if distance <= dist:
                G.add_edge(v[i], v[j], weight=distance)
            j += 1
    return G


'''
At this
'''
def Graph(dist=1000):
    url = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_information'
    bicing = pd.DataFrame.from_records(pd.read_json(url)['data']['stations'], index='station_id')
    if dist == 0:
        return Short_distance_Graph(bicing, dist)
    dist /= 1000
    sizex, sizey, lat_min, lon_min = Bbox_dimensions(bicing, dist)
    if sizex*sizey > 661500 or sizex*sizey < 7:
        return Create_by_sort_Graph(bicing, dist)
    M = Create_matrix(bicing, dist, sizex, sizey, lat_min, lon_min)
    return Create_linear_Graph(M, dist)

''' ********************************************************************************************************'''


'''
Given The graph "G" and a filename, creates an image of the graph on top of
the map of Barcelona and saves it with the given filename in the current
directory.
'''
def Plotgraph(G, filename):
    m_bcn = stm.StaticMap(1000, 1000)

    for node in G.nodes:
        marker = stm.CircleMarker((node.lon, node.lat), 'red', 3)
        m_bcn.add_marker(marker)

    for edge in G.edges:
        line = stm.Line(((edge[0].lon, edge[0].lat), (edge[1].lon, edge[1].lat)), 'blue', 1)
        m_bcn.add_line(line)

    image = m_bcn.render()
    image.save(filename)


'''
Puts all the indexes from the Nodes in the graph G in a list.
'''
def index_in_a_list(G):
    list = []
    for node in G.nodes():
        list.append(node.Index)
    return list


'''
For every station in the Graph, creates 3 nodes: A black one, which is the one
connected with the rest of the stations, a blue one representing the excess of
bikes (negative demand) and a red one representing the lack of bikes (positive demand).
Another node called 'TOP', is also created, this node compensates the flow, to
make the demand and offer sum to 0.
'''
def create_model(G, bidirected_G, bikes, requiredBikes, requiredDocks):
    G.add_node('TOP')
    demand = 0
    for st in bikes.itertuples():
        idx = st.Index
        if idx not in index_in_a_list(bidirected_G):
            continue
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
            G.edges[a_idx, n_idx]['capacity'] = 0

        elif req_docks > 0:
            demand -= req_docks
            G.nodes[a_idx]['demand'] = -req_docks
            G.edges[n_idx, r_idx]['capacity'] = 0
    G.nodes['TOP']['demand'] = -demand


'''
Adds the edges from our graph to the directed one.
'''
def add_edges_to_from(G, bidirected_G):
    for edge in bidirected_G.edges():
        node1 = edge[0]
        node2 = edge[1]
        id1 = node1.Index
        id2 = node2.Index
        peso = bidirected_G[node1][node2]['weight']
        G.add_edge('n'+str(id1), 'n'+str(id2), cost=int(1000*peso), weight=peso)
        G.add_edge('n'+str(id2), 'n'+str(id1), cost=int(1000*peso), weight=peso)


'''
Given the dictionary of dictionarys flowDict, returned by nx.network_simplex
and the directed graph G. Here we calculate and return the steps needed to guarantee the conditions,
the total cost in kilometers and the maximum cost in km*bikes per edge.
The maximum cost is represented by a tuple with the following format:
(cost in km*bikes, index of source station, index of destination station).
The steps is a list with tuples following this format:
(bikes to be moved, index of source station, index of destination station).
'''
def max_and_total_cost(G, flowDict):
    steps = []
    total_km = 0
    first = True
    for src in flowDict:
        if src[0] != 'n':
            continue
        idx_src = int(src[1:])
        for dst, b in flowDict[src].items():
            if dst[0] == 'n' and b > 0:
                idx_dst = int(dst[1:])
                total_km += G.edges[src, dst]['weight']
                cost = (G.edges[src, dst]['weight'] * b, idx_src, idx_dst)
                if first:
                    first = False
                    Max_cost = cost
                elif cost[0] > Max_cost[0]:
                    Max_cost = cost
                steps.append((b, idx_src, idx_dst))
    return steps, total_km, Max_cost


'''
Given the current graph we are working with and the number of required bikes and
docks for each station, this algorithm calculates the mimimum cost flow of bikes
between stations in the graph so that these requirements are guaranteed.
'''
def distribute(bidirected_G, requiredBikes, requiredDocks):
    url_status = 'https://api.bsmsa.eu/ext/api/bsm/gbfs/v2/en/station_status'
    bikes = pd.DataFrame.from_records(pd.read_json(url_status)['data']['stations'], index='station_id')
    G = nx.DiGraph()
    create_model(G, bidirected_G, bikes, requiredBikes, requiredDocks)
    add_edges_to_from(G, bidirected_G)
    err = False
    try:
        flowCost, flowDict = nx.network_simplex(G, weight='cost')

    except nx.NetworkXUnfeasible:
        err = True
        return [], 1, "malo", err
        '''
        "No solution could be found"
        '''

    except:
        err = True
        return [], 2, "malisimo", err
        '''
        "***************************************"
        "*** Fatal error: Incorrect graph model "
        "***************************************"
        '''

    if not err:
        steps, total_km, Max_cost = max_and_total_cost(G, flowDict)
        return steps, total_km, Max_cost, err
        '''
        "everything worked fine 😄"
        '''


'''
Given a time in hours, returns the time in (hours, minutes, seconds)
'''
def time_complete(t):
    h = int(t)
    d = (t - h) * 60
    m = int(d)
    s = int((d - m) * 60)
    return (h, m, s)


'''
Returns the number of connected components in G.
'''
def Components(G):
    return nx.number_connected_components(G)


'''
Returns the number of nodes in G.
'''
def Nodes(G):
    return nx.number_of_nodes(G)


'''
Returns the number of edges in G.
'''
def Edges(G):
    return nx.number_of_edges(G)


'''
Given The graph "G", a list representing a path and a filename,
creates an image of the path on top of the map of Barcelona and saves
it with the given filename in the current directory.
The parts where you should go by foot are represented with a orange line,
and the ones that you are suposed to go cycling with a blue line.
This function also returns the stimated time to do the route.
'''
def Plotpath_and_calculate_time(G, Path, filename):
        m_bcn = stm.StaticMap(1000, 1000)
        time = 0
        color = 'green'
        for i in range(len(Path) - 1):
            node1, node2 = Path[i], Path[i + 1]
            distance = haversine((node1.lat, node1.lon), (node2.lat, node2.lon))
            if G[node1][node2]['weight'] == distance:
                time += distance / 10
                line = stm.Line(((node1.lon, node1.lat), (node2.lon, node2.lat)), 'blue', 2)
            else:
                time += distance / 4
                line = stm.Line(((node1.lon, node1.lat), (node2.lon, node2.lat)), 'orange', 2)

            marker1 = stm.CircleMarker((node1.lon, node1.lat), color, 5)
            color = 'red'
            marker2 = stm.CircleMarker((node2.lon, node2.lat), color, 5)
            m_bcn.add_marker(marker1)
            m_bcn.add_marker(marker2)
            m_bcn.add_line(line)

        image = m_bcn.render()
        image.save(filename)
        return time_complete(time)


'''
Calculates the fastest route between the points coord1 and coord2 traveling
cycling around the graph G or walking on the complementary of the graph G.
Returns the estimated time to do the route and creates a picture of the path
with the given filename.
'''
def Route2(G, coord1, coord2, filename):
    start = Pandas(lat=coord1[0], lon=coord1[1])
    finish = Pandas(lat=coord2[0], lon=coord2[1])
    G.add_nodes_from([start, finish])
    Gc = nx.complement(G)
    G.remove_nodes_from([start, finish])
    for edge in Gc.edges:
        distance = haversine((edge[0].lat, edge[0].lon), (edge[1].lat, edge[1].lon))
        Gc.add_edge(edge[0], edge[1], weight=10/4 * distance)

    Gc = nx.compose(G, Gc)
    Shortest_Path = nx.dijkstra_path(Gc, start, finish)
    return Plotpath_and_calculate_time(Gc, Shortest_Path, filename)


'''
This is the route function asked for this project.
Calculates the fastest route between the points coord1 and coord2 traveling
cycling around the graph G and only walking twice: from the start point to the
first bicing station and from the last station to the finish point.
Returns the estimated time to do the route and creates a picture of the path
with the given filename.
'''
def Route1(G, coord1, coord2, filename):
    start = Pandas(lat=coord1[0], lon=coord1[1])
    finish = Pandas(lat=coord2[0], lon=coord2[1])
    max_dist = haversine((start.lat, start.lon), (finish.lat, finish.lon))
    G.add_nodes_from([start, finish])
    for node in G.nodes:
        distance1 = haversine((start.lat, start.lon), (node.lat, node.lon))
        distance2 = haversine((finish.lat, finish.lon), (node.lat, node.lon))
        if node != start and distance1 <= max_dist:
            G.add_edge(start, node, weight=10/4 * distance1)
        if node != finish and distance2 <= max_dist:
            G.add_edge(finish, node, weight=10/4 * distance2)
    Shortest_Path = nx.dijkstra_path(G, start, finish)
    time = Plotpath_and_calculate_time(G, Shortest_Path, filename)
    G.remove_nodes_from([start, finish])
    return time


'''
Returns the nearest bicing station from the coordinates "coord".
'''
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


'''
Given the nearest station, the coordinates of the point where we are and
a filename, creates an image with those points and a line between them.
'''
def Plotgraph_graph_to_nearest(n_station, coord, filename):
    m_bcn = stm.StaticMap(1000, 1000)
    line = stm.Line(((coord[1], coord[0]), (n_station.lon, n_station.lat)), 'orange', 2)
    marker1 = stm.CircleMarker((coord[1], coord[0]), 'green', 5)
    marker2 = stm.CircleMarker((n_station.lon, n_station.lat), 'red', 5)
    m_bcn.add_marker(marker1)
    m_bcn.add_marker(marker2)
    m_bcn.add_line(line)
    image = m_bcn.render()
    image.save(filename)


'''
Returns the adress of the nearest station to the coordinates of the user and the
expected time to go there by foot.
'''
def Nearest_station(G, coord, filename):
    n_station = Find_nearest_station(G, coord)
    Plotgraph_graph_to_nearest(n_station, coord, filename)
    time = time_complete(haversine((coord[0], coord[1]), (n_station.lat, n_station.lon)) / 4)
    return n_station.address, time
