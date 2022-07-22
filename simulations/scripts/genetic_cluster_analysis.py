import networkx as nx
import matplotlib.pyplot as plt
from social_epi import nx_conversion as nxc
import numpy as np
import os,json


def get_genetic_cluster_distribution(tn93_file,tn_file):
    gn = nxc.tn93distances2nx(tn_file,tn93_file,new_threshold=False)
    clusters = [len(c) for c in sorted(nx.connected_components(gn), key=len, reverse=True)]
    distribution = {int(cs) : clusters.count(cs) for cs in set(clusters)}
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


def summary_stats(distributions,save_dist_file):
    clusters = {int(key) : np.mean(val) for key,val in distributions.items()}
    json.dump(clusters,open(os.path.expanduser(save_dist_file),"w"))
    return clusters


def view_stats(clusters,upper_xlim=None,upper_ylim=None):
    cluster_sizes,mean_occurrence = zip(*sorted(clusters.items()))
    plt.bar(cluster_sizes,mean_occurrence)
    if upper_xlim:
        num_outliers = sum([v for c,v in clusters.items() if c > upper_xlim])
        print("The mass of the distribution above size {} is {}.".format(upper_xlim,num_outliers))
        plt.xlim([0,upper_xlim])
    if upper_ylim:
        plt.ylim([0,upper_ylim])
    plt.show()


def get_tn93_files(networks_folder):
    all_files = []
    for dir in os.listdir(networks_folder):
        full_dir = os.path.join(networks_folder,dir)
        tn93file = os.path.join(full_dir,"tn93_distances.csv")
        tnfile =  os.path.join(full_dir,"transmission_network.txt")
        all_files.append((tn93file,tnfile))
    return all_files


def analyze(networks_folder,savename,upper_xlim,upper_ylim):
    list_tn93_files = get_tn93_files(networks_folder)
    all_cluster_distributions = collate_results(list_tn93_files)
    clusters = summary_stats(all_cluster_distributions,savename)
    view_stats(clusters,upper_xlim,upper_ylim)
    return clusters


if __name__ == "__main__":
    # # compute cluster distribution
    # base = os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/study_params_20220722/")
    # networks_folder = os.path.join(base,"results_trimmed/JOB555814")
    savename = os.path.join(base,"genetic_cluster_distribution.json")
    # clusters = analyze(networks_folder,savename,100,300)

    # graph only
    clusters = json.load(open(savename))
    clusters = {int(c):v for c,v in clusters.items()}
    view_stats(clusters,upper_xlim=250,upper_ylim=None)


