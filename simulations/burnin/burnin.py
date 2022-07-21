from social_epi import sampling_social_networks as ssn
from social_epi import nx_conversion as nxc
from social_epi import CCMnet_constr_py as ccm
import numpy as np
import matplotlib.pyplot as plt
import json


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
    assess_burnin_L1("burnin_config.json","contact_network.txt","transmission_network.txt")
