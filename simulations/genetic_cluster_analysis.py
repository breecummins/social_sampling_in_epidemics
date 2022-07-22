import networkx as nx
import matplotlib.pyplot as plt
from social_epi import nx_conversion as nxc
import numpy as np
import os,json


def get_genetic_cluster_distribution(tn93_file,tn_file):
    gn = nxc.tn93distances2nx(tn93_file,new_threshold=False)
    tn,_ = nxc.favitestransmission2nx(tn_file)
    gn.add_nodes_from(tn)
    print(gn.number_of_nodes())
    clusters = [len(c) for c in sorted(nx.connected_components(gn), key=len, reverse=True)]
    distribution = {cs : clusters.count(cs) for cs in set(clusters)}
    return distribution


def collate_results(list_tn93_files):
    all_dists = [get_genetic_cluster_distribution(*f) for f in list_tn93_files]
    M = max([max(d) for d in all_dists])
    collated_dists = {i:[] for i in range(1,M)}
    for dist in all_dists:
        for key in collated_dists:
            if key in dist:
                collated_dists[key].append(dist[key])
            else:
                collated_dists[key].append(0)
    return collated_dists


def summary_stats(distributions):
    clusters = {int(key) : np.mean(val) for key,val in distributions.items()}
    json.dump(clusters,open(os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/20220713_study_params/genetic_cluster_distribution.json"),"w"))
    return clusters


def view_stats(clusters,upper_xlim):
    num_outliers = sum([c for c in clusters if c > upper_xlim])
    print("The number of clusters above size {} is {}.".format(upper_xlim,num_outliers))
    cluster_sizes,mean_occurrence = zip(*sorted(clusters.items()))
    plt.bar(cluster_sizes,mean_occurrence)
    plt.xlim([0,upper_xlim])
    plt.show()


def get_tn93_files():
    all_files = []
    base = os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/")
    networks_folder = os.path.join(base,"20220713_study_params/results_trimmed/JOB549929")
    for dir in os.listdir(networks_folder):
        full_dir = os.path.join(networks_folder,dir)
        tn93file = os.path.join(full_dir,"tn93_distances.csv")
        tnfile =  os.path.join(full_dir,"transmission_network.txt")
        all_files.append((tn93file,tnfile))
    return all_files


def analyze(upper_xlim):
    list_tn93_files = get_tn93_files()
    all_cluster_distributions = collate_results(list_tn93_files)
    clusters = summary_stats(all_cluster_distributions)
    view_stats(clusters,upper_xlim)
    return clusters


if __name__ == "__main__":
    clusters = analyze(60)


