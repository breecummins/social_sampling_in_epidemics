import networkx as nx
import pandas as pd


def tn93distances2nx(tn93_distance_file,new_threshold=False):
    '''
    Takes the distance csv produced by tn93 and generates a genetic cluster graph in networkx format. 

    The input new_threshold is either False, meaning use the same distance threshold used to create the tn93 file to identify edges, or is a float smaller than the tn93 distance threshold. The data will be altered to compute clusters with this smaller threshold. 

    ''' 
    df = pd.read_csv(tn93_distance_file)
    if new_threshold != False:
        df = df[df["Distance"] <= new_threshold]
    nodes1 = [int(s.split("|")[1]) for s in df["ID1"].values]
    nodes2 = [int(s.split("|")[1]) for s in df["ID2"].values]
    nodes = set(nodes1).union(set(nodes2))
    edges = zip(nodes1,nodes2)
    GCN = nx.Graph()
    GCN.add_nodes_from(nodes)
    GCN.add_edges_from(edges)
    GCN = GCN.to_directed()
    GCN = nx.transitive_closure(GCN)
    GCN = GCN.to_undirected()
    return GCN


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


def initial_graph2nx(degree_distribution,number_of_edges,number_of_nodes):
    # Degree distribution is probability of a node of degree x
    # same format as for sampling_social_networks config
    # number_of_edges and number_of_nodes is the size of the desired initial graph

    # pad distribution with zeros
    for k in range(number_of_nodes):
        if k not in degree_distribution:
            degree_distribution[k] = 0
    # make degree sequence
    degree_sequence = [int(i*number_of_edges) for i in sorted(degree_distribution).values]
    #IG = nx.configuration_model()
    



