import networkx as nx
import pandas as pd
import random, copy, json
from social_epi import CCMnet_constr_py as ccm
from social_epi import nx_conversion as nxconvert


def construct_overlap_network(config,network):
    '''
    Fix a subgraph of the contact network that will also appear in the social network.
    '''
    num_nodes = network.number_of_nodes()
    seed_prop = config["network_overlap"]
    num_seed_edges = int(seed_prop*network.number_of_edges())
    random_selection = random.sample(network.edges(), num_seed_edges)
    P = nx.Graph()
    P.add_nodes_from(network.nodes())
    P.add_edges_from(random_selection)
    return P, num_nodes


def gen_config(config,network): 
    '''
    This function is for transparency. I want the names of the CCM inputs to be clear.
    '''   
    P,pop = construct_overlap_network(config,network)
    deg_dist,_ = nxconvert.pad_deg_dist(config["deg_dist"],pop)
    G,Gfname = nxconvert.social_initial(config,pop,P)
    CCM_config = copy.deepcopy(config)
    CCM_config["samplesize"] = 1
    CCM_config["statsonly"] = True
    CCM_config["Network_stats"] = ["Degree"]
    # The following is not needed for "Degree" but could be needed later
    CCM_config["Prob_Distr"] = ["Multinomial_Poisson"]
    CCM_config["Prob_Distr_Params"] = [0,deg_dist]
    CCM_config["population"] = pop 
    CCM_config["G"] = Gfname
    CCM_config["P"] = nxconvert.nx2pandas(P)
    CCM_config["covPattern"] = []
    CCM_config["bayesian_inference"] = 0
    CCM_config["Ia"] = []
    CCM_config["Il"] = []
    CCM_config["R"] = []
    CCM_config["epi_params"] = []
    CCM_config["print_calculations"] = False
    CCM_config["use_G"] = 1
    CCM_config["outfile"] = "favites"
    return CCM_config


def run(contact_network_file,config_file,transmission_network_file=None,socialsavename="social_network.json"):
    # contact_network_file is the (unzipped) sexual contact network file from FAVITES
    # OR a networkx graph
    # config_file is a path to the sampling social networks configuration json
    # transimission_network is the (unzipped) transmission network file from FAVITES,
    # may be 'None' if networkx contact network is provided
    # savename is the file name where the social network will be stored  
    # network can be recovered with
    # network = nx.adjacency_graph(json.load(open(savename)))

    if isinstance(contact_network_file,str):
        contact_network,_ = nxconvert.favitescontacttransmission2nx(contact_network_file,transmission_network_file)
    else:
        contact_network =contact_network_file
    config = json.load(open(config_file))
    # make CCM config dictionary and then run CCM
    ccmc = gen_config(config,contact_network)
    social_network = ccm.CCMnet_constr_py(ccmc["Network_stats"],
                          ccmc["Prob_Distr"],
                          ccmc["Prob_Distr_Params"], 
                          ccmc["samplesize"],
                          ccmc["burnin"], 
                          ccmc["interval"],
                          ccmc["statsonly"], 
                          ccmc["G"],
                          ccmc["P"],
                          ccmc["population"], 
                          ccmc["covPattern"],
                          ccmc["bayesian_inference"],
                          ccmc["Ia"], 
                          ccmc["Il"], 
                          ccmc["R"], 
                          ccmc["epi_params"],
                          ccmc["print_calculations"],
                          ccmc["use_G"],
                          ccmc["outfile"])
    # add hiv status to each node
    nx.set_node_attributes(social_network,nx.get_node_attributes(contact_network,"hiv_status"),name="hiv_status")
    # save the network
    df = nxconvert.nx2pandas(social_network)
    df.to_csv(socialsavename,index=False)
    return social_network


    
