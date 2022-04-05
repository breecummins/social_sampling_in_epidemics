import networkx as nx
import random, copy, itertools, json
from social_epi import CCMnet_constr_py as ccm
from social_epi import epi_parsers as parse


def construct_seed_network(config,network):
    '''
    Fix a subgraph of the contact network as the seed for CCM sampling.
    '''
    num_nodes = network.number_of_nodes()
    pop_prop = config["population_increase"]
    pop = int(pop_prop*num_nodes)
    seed_prop = config["subnetwork_seed_proportion"]
    num_seed_edges = int(seed_prop*network.size())
    G = nx.Graph()
    G.add_nodes_from(network.nodes())
    random_selection = random.sample(network.edges(), num_seed_edges)
    G.add_edges_from(random_selection)
    #FIXME: add demographics to the new nodes?
    G.add_nodes(range(num_nodes,pop))
    return G, pop


def compute_degree_dist(network,pop):
    '''
    Return a list of probabilities of degrees in order [0,1,...,pop-1]
    '''
    deg_seq = sorted(d for _, d in network.degree())
    deg_dict = {}
    for d,g in itertools.groupby(deg_seq):
        deg_dict[d] = len(list(g))
    for k in range(pop):
        if k not in deg_dict or (k in deg_dict and deg_dict[k] == 0):
            # need to avoid zero values in deg dist for computational reasons
            deg_dict[k] = 1e-6
    dd = sorted(list(deg_dict.items()))
    deg_dist = [c/pop for _,c in dd]
    return deg_dist


def gen_config(config,network):    
    G,pop = (config,network)
    deg_dist = compute_degree_dist(network,pop)
    CCM_config = copy.deepcopy(config)
    CCM_config["samplesize"] = 1
    CCM_config["stats_only"] = True
    CCM_config["Network_stats"] = ["Degree"]
    # The following is not needed for "Degree" but could be needed later
    CCM_config["Prob_Distr"] = ["Multinomial_Poisson"]
    CCM_config["Prob_Distr_Params"] = [0,deg_dist]
    CCM_config["population"] = pop
    CCM_config["G"] = G
    CCM_config["P"] = G
    CCM_config["covPattern"] = None
    CCM_config["bayesian_inference"] = 1
    CCM_config["Ia"] = None
    CCM_config["Il"] = None
    CCM_config["R"] = None
    CCM_config["epi_params"] = None
    CCM_config["print_calculations"] = False
    CCM_config["use_G"] = 1
    CCM_config["outfile"] = "favites"
    return CCM_config


def save_social_network(social_network,savename):
    format2save = nx.adjacency_data(social_network)
    json.dump(format2save,open(savename,"w"))
    # network can be recovered with
    # network = nx.adjacency_graph(json.load(open(savename)))


def run(contact_network_file,config_file,savename="social_network.json"):
    # contact_network_file is the (unzipped) file from FAVITES
    # open files
    contact_network = parse.parse_contact_network_file(contact_network_file)
    config = json.load(open(config_file))
    # make CCM config dictionary and then run CCM
    ccmc = gen_config(contact_network,config)
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
    # drop social isolates not in contact network, only 
    # relevant when an increase in population size has been 
    # requested
    # this does change the size of the social network
    num_nodes = contact_network.number_of_nodes()
    if social_network.number_of_nodes() > num_nodes:
        for i in list(nx.isolates(social_network)):
            if isinstance(i,int) and i >= num_nodes:
                social_network.remove_node(i)
    save_social_network(social_network,savename)
    return social_network


    
