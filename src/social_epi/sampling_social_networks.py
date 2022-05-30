import networkx as nx
import pandas as pd
import random, copy, json
from social_epi import CCMnet_constr_py as ccm
from social_epi import nx_conversion as nxconvert


def construct_overlap_network(config,network):
    '''
    Fix a subgraph of the contact network that will also appear in the social network.
    '''
    seed_prop = config["network_overlap"]
    num_seed_edges = int(seed_prop*network.number_of_edges())
    random_selection = random.sample(network.edges(), num_seed_edges)
    P = nx.Graph()
    P.add_nodes_from(network.nodes())
    P.add_edges_from(random_selection)
    return P


def gen_config(config,network): 
    '''
    This function builds a CCM config dictionary.
    '''   
    pop = network.number_of_nodes()
    G = nxconvert.initial_graph_from_configuration_model(config,pop)
    CCM_config = copy.deepcopy(config)
    CCM_config["samplesize"] = 1
    CCM_config["statsonly"] = True
    CCM_config["Network_stats"] = ["Degree"]
    CCM_config["population"] = pop
    CCM_config["G"] = G
    CCM_config["use_G"] = 1
    CCM_config["outfile"] = "favites"
    # The following is not needed for "Degree" but could be needed later
    CCM_config["Prob_Distr"] = ["Multinomial_Poisson"]
    CCM_config["Prob_Distr_Params"] = [0]
    # All the following are not used
    CCM_config["P"] = None
    CCM_config["covPattern"] = []
    CCM_config["bayesian_inference"] = 0
    CCM_config["Ia"] = []
    CCM_config["Il"] = []
    CCM_config["R"] = []
    CCM_config["epi_params"] = []
    CCM_config["print_calculations"] = False
    return CCM_config


def run(config_file,contact_network_file,transmission_network_file=None):
    # config_file is a path to the sampling social networks configuration json
    # contact_network_file is the (unzipped) sexual contact network file from FAVITES OR a networkx graph
    # transmission_network is the (unzipped) transmission network file from FAVITES,
    # may be 'None' if networkx contact network is provided

    if isinstance(contact_network_file,str):
        contact_network,_ = nxconvert.favitescontacttransmission2nx(contact_network_file,transmission_network_file)
    else:
        contact_network =contact_network_file
    config = json.load(open(config_file))
    # make CCM config dictionary and then run CCM
    ccmc = gen_config(config,contact_network)
    social_network = ccm.CCMnet_constr_py(ccmc)
    # union with fixed network
    P = construct_overlap_network(config,contact_network)
    social_network.add_edges_from(P.edges())
   # add hiv status to each node
    nx.set_node_attributes(social_network,nx.get_node_attributes(contact_network,"hiv_status"),name="hiv_status")
    return social_network, P


if __name__ == "__main__":
    import sys
    configfile= sys.argv[1]
    contact_network_file = sys.argv[2]
    transmission_network_file = sys.argv[3]
    contact_network,_ = nxconvert.favitescontacttransmission2nx(contact_network_file,transmission_network_file)
    config = json.load(open(configfile))
    P = construct_overlap_network(config,contact_network)
    P = nxconvert.nx2pandas(P)
    P.to_csv("fixed_subgraph.csv",index=False)
    G,Gfname = nxconvert.initial_graph_from_configuration_model(config,contact_network.number_of_nodes())
    
