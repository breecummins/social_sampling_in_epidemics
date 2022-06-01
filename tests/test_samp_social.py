from social_epi import sampling_social_networks as ssn
from social_epi import nx_conversion as nxc
import numpy as np
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


if __name__ == "__main__":
    # cd tests/chain_test/FAVITES_output_20220524141705
    social_config = "../../../src/configs/sampling_social_networks_config.json"
    contact_network = "contact_network.txt"
    transmission_network = "error_free_files/transmission_network.txt"
    burnin_list = [100000, 150000, 200000]
    determine_burnin(social_config,contact_network,transmission_network,burnin_list)