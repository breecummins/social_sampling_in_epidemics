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


def favitescontact2nx(contact_network_file):
    # Parse FAVITES contact network format into a networkx graph
    f = open(contact_network_file)
    CG = nx.Graph()
    for l in f.readlines():
        words = l.split()
        if words[0] == "NODE":
            CG.add_node(words[1])
        elif words[0] == "EDGE":
            CG.add_edge(words[1],words[2])
    return CG


def favitestransmission2nx(transmission_network_file):
    # Parse FAVITES transmission network format into a networkx graph
    df = pd.read_csv(transmission_network_file,sep="\t",header=None)
    TG = nx.Graph()
    nodes = df[1].values
    TG.add_nodes_from(nodes)
    # get rid of seed nodes where no transmission took place
    df = df[df[0] != "None"]
    edges = zip(df[0].values,df[1].values)
    TG.add_edges_from(edges)
    return TG
    



