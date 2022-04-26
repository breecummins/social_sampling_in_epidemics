import networkx as nx
import pandas as pd


def tn93distances2nx(tn93_distance_file,new_threshold=False):
    '''
    Takes the distance csv produced by tn93 and generates a networkx graph. 

    The input new_threshold is either False, meaning use the same distance threshold used to create the tn93 file to identify edges, or is a float smaller than the tn93 distance threshold. The data will be altered to have edges only between nodes with this smaller threshold. 

    ''' 
    df = pd.read_csv(tn93_distance_file)
    if new_threshold != False:
        df = df[df["Distance"] <= new_threshold]
    nodes1 = [int(s.split("|")[1]) for s in df["ID1"].values]
    nodes2 = [int(s.split("|")[1]) for s in df["ID2"].values]
    nodes = set(nodes1).union(set(nodes2))
    edges = zip(nodes1,nodes2)
    GN = nx.Graph()
    GN.add_nodes_from(nodes)
    GN.add_edges_from(edges)
    return GN


def favitescontacttransmission2nx(contact_network_file,transmission_network_file):
    # Parse FAVITES contact and transmission networks formats into networkx graphs
    TG,hiv_pos_nodes = favitestransmission2nx(transmission_network_file)
    f = open(contact_network_file)
    CG = nx.Graph()
    for l in f.readlines():
        words = l.split()
        if words[0] == "NODE":
            node = int(words[1])
            if node in hiv_pos_nodes:
                hiv=1
            else:
                hiv=0
            CG.add_node(node,hiv_status=hiv)
        elif words[0] == "EDGE":
            CG.add_edge(int(words[1]),int(words[2]))
    return CG, TG


def favitestransmission2nx(transmission_network_file):
    # Parse FAVITES transmission network format into a networkx graph
    df = pd.read_csv(transmission_network_file,sep="\t",header=None)
    TG = nx.Graph()
    nodes = list(map(int,df[1].values))
    TG.add_nodes_from(nodes)
    # get rid of seed nodes where no transmission took place
    df = df[df[0] != "None"]
    edges = zip(list(map(int,df[0].values)),list(map(int,df[1].values)))
    TG.add_edges_from(edges)
    return TG, nodes
    



