import pandas
import networkx as nx
from jutge import read

def main():
    G = nx.DiGraph()
    G.add_edge(1,3)
    print(G.number_of_nodes())
    print(list(G.nodes))
main()

# prueba
