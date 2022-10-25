from social_epi import nx_conversion as nxc
import os

def compute_overlap(transmission_network_file,tn93_distance_file):
    tn,_ = nxc.favitestransmission2nx(transmission_network_file)
    gn = nxc.tn93distances2nx(transmission_network_file,tn93_distance_file,new_threshold=False)
    size_overlap = len(set(tn.edges).intersection(gn.edges))
    return size_overlap, tn.number_of_edges()


if __name__ == "__main__":
    import sys
    size_overlap, num_tn_edges = compute_overlap(sys.argv[1],sys.argv[2])
    print("Number of overlap edges: {}".format(size_overlap))
    print("Number of TN edges: {}".format(num_tn_edges))
    print("Proportion of TN edges: {}".format(size_overlap/num_tn_edges))