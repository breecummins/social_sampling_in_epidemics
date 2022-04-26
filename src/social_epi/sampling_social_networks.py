import networkx as nx
import random, copy, itertools, json
from social_epi import CCMnet_constr_py as ccm
from social_epi import nx_conversion as nxconvert


def construct_seed_network(config,network):
    '''
    Fix a subgraph of the contact network as the seed for CCM sampling.
    '''
    num_nodes = network.number_of_nodes()
    seed_prop = config["subnetwork_seed_proportion"]
    num_seed_edges = int(seed_prop*network.size())
    G = nx.Graph()
    G.add_nodes_from(network.nodes())
    random_selection = random.sample(network.edges(), num_seed_edges)
    G.add_edges_from(random_selection)
    return G, num_nodes


def compute_degree_dist(network,pop):
    '''
    Return a list of probabilities of degrees in order [0,1,...,pop-1] generated from the input network.
    '''
    deg_seq = sorted(d for _, d in network.degree())
    deg_dict = {}
    for d,g in itertools.groupby(deg_seq):
        deg_dict[d] = len(list(g))/pop
    deg_dist = pad_deg_dist(deg_dict,pop)
    return deg_dist


def pad_deg_dist(deg_dict,pop):
    '''
    Given the nonzero values of a degree distribution, pad all remaining degree sizes with a small probability
    '''
    for k in range(pop):
        if k not in deg_dict or (k in deg_dict and deg_dict[k] == 0):
            # need to avoid zero values in deg dist for computational reasons
            deg_dict[k] = 1e-6/pop
    dd = sorted(list(deg_dict.items()))
    deg_dist = [c for _,c in dd]
    return deg_dist


def gen_config(config,network):    
    G,pop = construct_seed_network(config,network)
    if "degree_distribution" not in config:
        deg_dist = compute_degree_dist(network,pop)
    else:
        deg_dict = { int(k) : v for k,v in config["degree_distribution"].items() }
        deg_dist = pad_deg_dist(deg_dict,pop)
    CCM_config = copy.deepcopy(config)
    CCM_config["samplesize"] = 1
    CCM_config["statsonly"] = True
    CCM_config["Network_stats"] = ["Degree"]
    # The following is not needed for "Degree" but could be needed later
    CCM_config["Prob_Distr"] = ["Multinomial_Poisson"]
    CCM_config["Prob_Distr_Params"] = [0,deg_dist]
    CCM_config["population"] = pop
    df = nx.to_pandas_edgelist(G,dtype=int) 
    CCM_config["G"] = df
    CCM_config["P"] = df
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


def save_social_network(social_network,savename):
    format2save = nx.adjacency_data(social_network)
    json.dump(format2save,open(savename,"w"))
    # network can be recovered with
    # network = nx.adjacency_graph(json.load(open(savename)))


def run(contact_network_file,transmission_network_file,config_file,savename="social_network.json"):
    # contact_network_file is the (unzipped) sexual contact network file from FAVITES
    # transimission_network is the (unzipped) transmission network file from FAVITES
    # open files
    contact_network,_ = nxconvert.favitescontacttransmission2nx(contact_network_file,transmission_network_file)
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
    save_social_network(social_network,savename)
    return social_network


    
