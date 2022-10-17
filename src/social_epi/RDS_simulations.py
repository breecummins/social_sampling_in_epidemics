import networkx as nx
import pandas as pd
import numpy as np
import random as rand
import pandas as pd
import warnings


def RDS(net,waves,coupons,p,size,seeds,posseed,poswave):
    """Conducts respondent-driven sampling
    
    Input:
       net:       network, networkx graph
       waves:     maximum number of waves, integer (use 0 with poswave=True for contract tracing)
       coupons:   number of coupons per respondent, integer
       p:         probability of participation, float
       size:      target sample size
       seeds:     number of seeds
       posseed:   whether the seed should be HIV-positive, boolean, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for net
       poswave:   whether recruitment continues past wave limit for positive agents, boolean, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for net
    
    Output:
        sampled: list of sampled nodes
    """
    
    #Check if HIV status is needed
    if posseed or poswave:
        #Check for missing HIV status node attribute
        if nx.get_node_attributes(net,"hiv_status")=={}:
            #Warning
            warnings.warn('Warning Message: no node attribute "hiv_status", posseed and poswave set to False')
            #Set posseed to False
            posseed=False
            #Set poswave to False
            poswave=False
    #Count number of nodes
    n=np.shape(net)[0]
    #Initialize sample
    sample={}
    #Initialize list of already sampled agents
    sampled=[]
    #Check for HIV positive seed
    if posseed:
        #Choose seeds from HIV positive nodes
        seed=rand.choices([x for x,y in net.nodes(data=True) if y['hiv_status']==1],k=seeds)
    #Random seed
    else:
        #Choose seeds from all nodes
        seed=rand.choices(list(range(n)),k=seeds)

    # ########
    # # test -- delete when done
    # hiv = nx.get_node_attributes(net, "hiv_status")
    # print("Number HIV+ seeds: {} out of {} seeds".format(len([x for x in seed if hiv[x]]),len(seed)))
    # print("Total number HIV+ in population: {} out of 15,397".format(sum([y["hiv_status"] for _,y in net.nodes(data=True)] )))
    # ##########

    #Store seeds as 0th wave
    sample[0]=seed
    #Add seed to list of sampled agents
    sampled=sampled+seed
    #Initilaize wave counter
    wave=0
    #Initilaize count of nodes sampled
    nodes=len(sampled) 
    #Check for waves still to be completed, unsampled nodes, nodes sampled in previous wave, and under target sample size
    while wave<waves and nodes<n and sample[wave]!=[] and nodes<size:
        #Increase wave counter
        wave=wave+1
        #Initialize list of nodes sampled in current wave
        sample[wave]=[]
        #loop through nodes sampled in previous wave
        for i in sample[wave-1]:
            #Identify neighbors of node i
            nbrs=list(net[i])
            #Remove already sampled nodes
            nbrs=list(set(nbrs)-set(sampled)) 
            #Initialize count of used coupons
            used=0
            #Check for unsampled nodes and remaining coupons
            while used<coupons and nbrs!=[]:
                #Sample one node from list of neighbors
                node=rand.choice(nbrs)
                #Probability check on node participation
                if np.random.uniform(0,1)<p:
                    #Add sampled node to list of nodes sampled during current wave
                    sample[wave]=sample[wave]+[node]
                    #Add sampled node to list of sampled nodes
                    sampled=sampled+[node]
                    #Increase counter for sampled nodes
                    nodes=nodes+1
                    #Increase count of used coupons
                    used=used+1
                    #Remove node from list of neighbors
                    nbrs.remove(node)
                else:
                    #Remove node from list of neighbors
                    nbrs.remove(node)
            if nodes >= size:
                break        
    #Check for continuing past final wave for HIV-positive agents
    if poswave:
        #Create network from last wave
        last=nx.subgraph(net,sample[wave])
        #Generate list of HIV-positive nodes in last wave
        positive=[x for x,y in last.nodes(data=True) if y['hiv_status']==1]
        #Check for HIV-positive nodes in last wave, unsampled nodes, and nodes sampled in previous wave
        while positive!=[] and nodes<n and sample[wave]!=[]:
            wave=wave+1
            #Initialize list of nodes sampled in current wave
            sample[wave]=[]
            #loop through nodes sampled in previous wave
            for i in positive:
                #Identify neighbors of node i
                nbrs=list(net[i])
                #Remove already sampled nodes
                nbrs=list(set(nbrs)-set(sampled)) 
                #Initialize count of used coupons
                used=0
                #Check for unsampled nodes and remaining coupons
                while used<coupons and nbrs!=[]:
                    #Sample one node from list of neighbors
                    node=rand.choice(nbrs)
                    #Probabilioty check on node participation
                    if np.random.uniform(0,1)<p:
                        #Add sampled node to list of nodes sampled during current wave
                        sample[wave]=sample[wave]+[node]
                        #Add sampled node to list of sampled nodes
                        sampled=sampled+[node]
                        #Increase counter for sampled nodes
                        nodes=nodes+1
                        #Increase count of used coupons
                        used=used+1
                        #Remove node from list of neighbors
                        nbrs.remove(node)
                    else:
                        #Remove node from list of neighbors
                        nbrs.remove(node)
            #Create network from last wave
            last=nx.subgraph(net,sample[wave])
            #Generate list of HIV-positive nodes in last wave
            positive=[x for x,y in last.nodes(data=True) if y['hiv_status']==1]
                
    return sampled


def CountPairs(net,sampled):
    """Counts number of pairs in network included in sample
    
    Input:
       net:     network, networkx graph
       sampled: list of sampled nodes
    
    Output:
        count: count of links between sampled nodes
        total: total links in net
    """
    #Count number of edges in network
    total=net.number_of_edges()
    #Create a subnetwork with only sampled nodes
    subnet=nx.subgraph(net,sampled)
    #Count number of edges in subnetwork
    count=subnet.number_of_edges()
    
    return count,total


def Assess(GN,TN,SN,CN,param_dict):
    """Assesses pairs recruited
    
    Input:
       GN:          genetic cluster network, networkx graph
       TN:          transmission network, networkx graph
       SN:          social network, networkx graph
       CN:          contact network, networkx graph
       Keys in param_dict:
       SNwaves:     maximum number of waves for social network, integer
       CNwaves:     maximum number of waves for contact network, integer
       SNcoupons:   number of coupons per respondent for social network, integer
       CNcoupons:   number of coupons per respondent for contact network, integer
       SNprob:         probability of participation for social network, float
       CNprob:         probability of participation for contact network, float
       SNsize: target sample size for social network sampling
       CNsize: target sample size for contact network sampling 
       SNseeds: number of seeds to start the social network RDS
       CNseeds: number of seeds to start the contact network RDS
       SNposseed:  True or False, whether the seed for social network should be HIV-positive, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for SN
       CNposseed:  True or False, whether the seed for contact network should be HIV-positive, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for CN
       SNposwave: True or False, whether recruitment continues past wave limit in social network for positive agents, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for the social network
       CNposwave: True or False, whether recruitment continues past wave limit in contact network for positive agents, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for the contact network 
       savename: "path/to/filename" in which to save results
    
    Output:
       row:         row of dataframe is JSON format
    """
    
    keys=['SNwaves','CNwaves','SNcoupons','CNcoupons','SNprob','CNprob','SNsize','CNsize','SNseeds','CNseeds','SNposseed','CNposseed','SNposwave','CNposwave','savename']
    SNwaves,CNwaves,SNcoupons,CNcoupons,SNprob,CNprob,SNsize,CNsize,SNseeds,CNseeds,SNposseed,CNposseed,SNposwave,CNposwave,savename=[param_dict.get(key) for key in keys]
    
    # print("Social")
    SNsampled=RDS(SN,SNwaves,SNcoupons,SNprob,SNsize,SNseeds,SNposseed,SNposwave)
    # print("Contact")
    CNsampled=RDS(CN,CNwaves,CNcoupons,CNprob,CNsize,CNseeds,CNposseed,CNposwave)
    
    SNGNcount,SNGNtotal=CountPairs(GN,SNsampled)
    CNGNcount,CNGNtotal=CountPairs(GN,CNsampled)
    SNTNcount,SNTNtotal=CountPairs(TN,SNsampled)
    CNTNcount,CNTNtotal=CountPairs(TN,CNsampled)

    # how many sampled are HIV+
    SN_num_hiv_pos = len([x for x in SNsampled if SN.nodes[x]['hiv_status']==1])
    CN_num_hiv_pos = len([x for x in CNsampled if CN.nodes[x]['hiv_status']==1])
    
    row={
        "SN GN count": [SNGNcount],
        "SN GN total": [SNGNtotal],
        "CN GN count": [CNGNcount],
        "CN GN total": [CNGNtotal],
        "SN TN count": [SNTNcount],
        "SN TN total": [SNTNtotal],
        "CN TN count": [CNTNcount],
        "CN TN total": [CNTNtotal],
        "SN sampled" : [SNsampled],
        "CN sampled" : [CNsampled],
        "SN HIV+"    : [SN_num_hiv_pos],
        "CN HIV+"    : [CN_num_hiv_pos]
        }
    
    row=pd.DataFrame(row)
    
    return row
