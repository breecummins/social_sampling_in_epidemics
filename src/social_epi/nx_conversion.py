import networkx as nx
import pandas as pd
import json,os


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
    # make the genetic cluster network that is composed of a collection of disconnected cliques
    GCN = GCN.to_directed()
    GCN = nx.transitive_closure(GCN)
    GCN = GCN.to_undirected()
    GCN.remove_edges_from(nx.selfloop_edges(GCN))
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


def nx2pandas(G):
    return nx.to_pandas_edgelist(G,dtype=int)


def pandas2nx(df):
    return nx.from_pandas_edgelist(df,edge_attr=True)


def pandasfile2nx(fname):
    df = pd.read_csv(fname)
    return pandas2nx(df)


def pad_deg_dist(deg_dict,small_prob,num_nodes):
    '''
    Given the nonzero values of a degree distribution, pad all remaining degree sizes with a small probability. 
    '''
    deg_dict = { int(k) : v for k,v in deg_dict.items() }
    deg_dist = []
    for k in range(num_nodes):
        if k not in deg_dict:
            # need to avoid zero values in deg dist for computational reasons
            deg_dist.append(small_prob)
        else:
            deg_dist.append(deg_dict[k]+small_prob)
    return deg_dist


def initial_graph_from_configuration_model(config,number_of_nodes):
    # retrieve degree distribution from hyper parameters
    if isinstance(config,str):
        config = json.load(open(config))    
    degree_distribution = pad_deg_dist(config["degree_distribution"],config["small_prob"],number_of_nodes)
    # make degree sequence 
    degree_sequence = []
    for d,p in enumerate(degree_distribution):
        degree_sequence.extend([d]*int(p*number_of_nodes))
    # configuration models need an even sum of degrees
    # if sum is odd, find the degree with the highest incidence and add 1 
    # (highest incidence will create least bias, I think, at least for large graphs)
    if sum(degree_sequence) % 2 != 0:
        k = degree_sequence.index(max(degree_sequence))
        degree_sequence[k] += 1
    # make configuration model without multi-edges or self-loops
    IG = nx.configuration_model(degree_sequence,create_using=nx.Graph)
    return nx2pandas(IG)


def reinflate_networks(contacttxt,transmissiontxt,tn93dists,socialcsv):    
    cn,tn = favitescontacttransmission2nx(contacttxt,transmissiontxt)
    gn = tn93distances2nx(tn93dists,new_threshold=False)
    sn = pandas2nx(pd.read_csv(socialcsv))
    sn.add_nodes_from(cn.nodes())
    nx.set_node_attributes(sn,nx.get_node_attributes(cn,"hiv_status"),name="hiv_status")
    return gn,tn,sn,cn




