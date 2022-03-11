import networkx as nx

def CountPairs(net,sampled):
    """Counts number of pairs in network included in sample
    
    Input:
       net:     network, networkx graph
       sampled: list of sampled nodes
    
    Output:
        count: count of links between sampled nodes
        total: total links in net
    """
    #Count number of edges in network
    total=net.number_of_edges()
    #Create a subnetwork with only sampled nodes
    subnet=nx.subgraph(net,sampled)
    #Count number of edges in subnetwork
    count=subnet.number_of_edges()
    
    return count,total