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


def pad_deg_dist(deg_dict,num_nodes):
    '''
    Given the nonzero values of a degree distribution, pad all remaining degree sizes with a small probability. 
    '''
    deg_dict = { int(k) : v for k,v in deg_dict.items() }
    deg_dist = []
    for k in range(num_nodes):
        if k not in deg_dict or (k in deg_dict and deg_dict[k] == 0):
            # need to avoid zero values in deg dist for computational reasons
            deg_dist.append(1e-6/num_nodes)
        else:
            deg_dist.append(deg_dict[k])
    return deg_dist,deg_dict


def initialgraph2nx(degree_distribution,number_of_nodes):
    # Degree distribution is probability of a node of degree x with the
    # same format as for sampling_social_networks config (a dictionary).
    # number_of_nodes is the size of the desired initial graph.
    # fixed_overlap_network is the subnetwork of the sexual network that is also in the social network;
    # it is a networkx Graph object.

    degree_distribution,_ = pad_deg_dist(degree_distribution,number_of_nodes)
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
    return IG


def social_initial(sn_config,number_of_nodes, fixed_overlap_network):
    if isinstance(sn_config,str):
        config = json.load(open(sn_config))
    else:
        config=sn_config
    IG = initialgraph2nx(config["deg_dist"],number_of_nodes)
    # take union of subgraph and config model
    IG.add_edges_from(fixed_overlap_network.edges())
    # save
    df = nx2pandas(IG)
    savename = config["sn_initial_savename"]
    df.to_csv(savename,index=False)
    return df, savename


def contact_initial(cn_config):
    config = json.load(open(cn_config))
    IG = initialgraph2nx(config["deg_dist"], config["num_nodes"])
    # save
    df = nx2pandas(IG)
    savename = config["cn_initial_savename"]
    df.to_csv(savename,index=False)
    return df,savename


def nx2pandas(G):
    return nx.to_pandas_edgelist(G,dtype=int)






