from social_epi import sampling_social_networks as ssn
from social_epi import nx_conversion as nxc
from social_epi import CCMnet_constr_py as ccm
import numpy as np
import matplotlib.pyplot as plt
import json,time


def determine_burnin(social_config, contact_network, transmission_network, burnin_list):
    config = json.load(open(social_config))
    for bu in burnin_list:
        starttime = time.time()
        config["burnin"] = bu
        print("Burnin: {}".format(bu))
        social_network, overlap_network = ssn.run(config, contact_network, transmission_network)
        print("The overlap network is conserved: {}".format(check_overlap(social_network,overlap_network)))
        print("Error in degree distribution: {}".format(compare_dists(config,social_network)))
        print("Time taken: {}".format(time.time()-starttime))


def check_overlap(SN,ON):
    return set(ON.edges()).issubset(set(SN.edges()))


def compare_dists(config,SN):
    N = SN.number_of_nodes()
    deg_dict = config["degree_distribution"]
    deg_dist = np.asarray(nxc.pad_deg_dist(deg_dict,config["small_prob"],N))
    sn_degs = [deg for _, deg in SN.degree()]
    sn_deg_dist = np.array([sn_degs.count(i)/N for i in range(N)])
    return sum(np.abs(deg_dist-sn_deg_dist))


def assess_burnin_L1(burnin_config_file,contact_network_file,transmission_network_file=None):
    if isinstance(contact_network_file,str):
        contact_network,_ = nxc.favitescontacttransmission2nx(contact_network_file,transmission_network_file)
    else:
        contact_network =contact_network_file
    if isinstance(burnin_config_file,str):
        config = json.load(open(burnin_config_file))
    else:
        config = burnin_config_file
    N=int(contact_network.number_of_nodes())
    # make CCM config dictionary and then run CCM
    ccmc = ssn.gen_config(config,N)
    _, dd_stats = ccm.CCMnet_constr_py(**ccmc)
    dd_stats.to_csv("deg_hist_results.csv")
    # get desired deg dist
    deg_dict = config["degree_distribution"]
    deg_dist = np.asarray(nxc.pad_deg_dist(deg_dict,config["small_prob"],N))
    L1 = []
    for dd in dd_stats.iterrows():
        dd = np.array(dd[1])
        L1.append(sum(np.abs(deg_dist-dd/N)))
    json.dump(L1,open("L1_results.json","w"))
    plt.scatter(range(len(L1)),L1)
    plt.savefig("convergence.png")
    plt.show()



if __name__ == "__main__":
    # cd tests/chain_test/FAVITES_output_20220524141705
    contact_network = "contact_network.txt"
    transmission_network = "error_free_files/transmission_network.txt"

    # social_config = "../../../src/configs/sampling_social_networks_config.json"
    # burnin_list = np.arange(1000,10000,1000)
    # determine_burnin2(social_config,contact_network,transmission_network,burnin_list)

    bc = "../../../src/configs/burnin_config.json"
    assess_burnin_L1(bc,contact_network,transmission_network)
