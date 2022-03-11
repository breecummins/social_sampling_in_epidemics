import networkx as nx
import random, copy, itertools, json
import CCMnet_constr_py as ccm


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
    Return a list of (normalized) counts of degrees in order [0,1,...,pop-1]
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
    N = sum(list(deg_dict.values()))
    # Ask Ravi: Should this be normalized or not?
    deg_dist = [c/N for _,c in dd]
    return deg_dist


def gen_config(config,network):    
    G,pop = (config,network)
    deg_dist = compute_degree_dist(network,pop)
    CCM_config = copy.deepcopy(config)
    CCM_config["Network_stats"] = ["Degree"]
    # Ravi, I don't need this for Degree, correct?
    CCM_config["Prob_Distr"] = [None]
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



def run(contact_network,config_file,savename="social_network.json"):
    # Need example output from FAVITES to get network format
    config = json.load(open(config_file))
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
    save_social_network(social_network,savename)
    return social_network


    
