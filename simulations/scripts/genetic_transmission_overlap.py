from social_epi import nx_conversion as nxc
import pandas as pd
import networkx as nx
import os

def compute_overlap(transmission_network_file,tn93_distance_file):
    tn,_ = nxc.favitestransmission2nx(transmission_network_file)
    gn = nxc.tn93distances2nx(transmission_network_file,tn93_distance_file,new_threshold=False)
    size_overlap = len(set(tn.edges).intersection(gn.edges))
    return size_overlap, tn.number_of_edges()


def get_tn93_distances_TN_edges_only(transmission_network_file,fasta_file):
    # create transmission network with only nodes that participated in a transmission event during the simulation
    df = pd.read_csv(transmission_network_file,sep="\t",header=None)
    TG = nx.Graph()
    # get rid of seed nodes where no transmission took place
    df = df[df[0] != "None"]
    edges = zip(list(map(int,df[0].values)),list(map(int,df[1].values)))
    edges = [sorted(e) for e in edges]
    print("Number of TN edges = {}".format(len(edges)))
    TG.add_edges_from(edges)
    nodes = TG.nodes()
    labels = ["|" +str(n)+ "|" for n in nodes]
    print("Number of TN nodes = {} < {}".format(len(labels),2*len(edges)))
    # get sequence for each individual
    lines = open(fasta_file).readlines()
    IDseq = list(zip(lines[::2], lines[1::2]))
    # filter sequences for those nodes in TN
    with open("filtered_sequences.fasta","w") as f:
        for id,seq in IDseq:
            if any([l in id for l in labels]):
                f.write(id)
                f.write(seq)
    idlabels = []
    for i,_ in IDseq:
        s = i.split("|")
        idlabels.append("|" + s[1] + "|")
    print("\nIntersection:\n")
    I = set(labels).intersection(idlabels)
    print(I)
    print("Number of nodes in intersection: {}".format(len(I)))
        
                  


if __name__ == "__main__":
    import sys
    # size_overlap, num_tn_edges = compute_overlap(sys.argv[1],sys.argv[2])
    # print("Number of overlap edges: {}".format(size_overlap))
    # print("Number of TN edges: {}".format(num_tn_edges))
    # print("Proportion of TN edges: {}".format(size_overlap/num_tn_edges))

    get_tn93_distances_TN_edges_only(sys.argv[1],sys.argv[2])