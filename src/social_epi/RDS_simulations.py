import networkx as nx
import pandas as pd
import numpy as np
import random as rand
import json, warnings


def RDS(net,waves,coupons,p,size,posseed=False,poswave=False):
    """Conducts respondent-driven sampling
    
    Input:
       net:       network, networkx graph
       waves:     maximum number of waves, integer (use 0 with poswave=True for contract tracing)
       coupons:   number of coupons per respondent, integer
       p:         probability of participation, float
       size:      target sample size
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
        #Choose seed from HIV positive nodes
        seed=rand.choice([x for x,y in net.nodes(data=True) if y['hiv_status']==1])
    #Random seed
    else:
        #Choose seed from all nodes
        seed=rand.randint(0,n-1)
    #Store seed as 0th wave
    sample[0]=[seed]
    #Add seed to list of sampled agents
    sampled.append(seed)
    #Initilaize wave counter
    wave=0
    #Initilaize count of nodes sampled
    nodes=1 
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


def Assess(dictionary):
    """Assesses pairs recruited
    
    Input:
       GN:          genetic cluster network, networkx graph
       TN:          transmission network, networkx graph
       SN:          social network, networkx graph
       CN:          contact network, networkx graph
       SNwaves:     maximum number of waves for social network, integer
       CNwaves:     maximum number of waves for contact network, integer
       SNcoupons:   number of coupons per respondent for social network, integer
       CNcoupons:   number of coupons per respondent for contact network, integer
       SNp:         probability of participation for social network, float
       CNp:         probability of participation for contact network, float
       SNpositive:  whether the seed for social network should be HIV-positive, boolean, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for SN
       SNpositive:  whether the seed for contact network should be HIV-positive, boolean, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for CN
    
    Output:
       row:         row of dataframe is JSON format
    """
    
    keys=['GN','TN','SN','CN','SNwaves','CNwaves','SNcoupons','CNcoupons','SNp','CNp','SNsize','CNsize','SNpositive','CNpositive','savename']
    GN,TN,SN,CN,SNwaves,CNwaves,SNcoupons,CNcoupons,SNp,CNp,SNsize,CNsize,SNpositive,CNpositive,savename=[dictionary.get(key) for key in keys]
    
    SNsampled=RDS(SN,SNwaves,SNcoupons,SNp,SNpositive)
    CNsampled=RDS(CN,CNwaves,CNcoupons,CNp,CNpositive)
    
    SNGNcount,SNGNtotal=CountPairs(GN,SNsampled)
    CNGNcount,CNGNtotal=CountPairs(GN,CNsampled)
    SNTNcount,SNTNtotal=CountPairs(TN,SNsampled)
    CNTNcount,CNTNtotal=CountPairs(TN,CNsampled)
    
    row={
        "SN GN count": SNGNcount,
        "SN GN total": SNGNtotal,
        "CN GN count": CNGNcount,
        "CN GN total": CNGNtotal,
        "SN TN count": SNTNcount,
        "SN TN total": SNTNtotal,
        "CN TN count": CNTNcount,
        "CN TN total": CNTNtotal,
        "SN waves": SNwaves,
        "CN waves": CNwaves,
        "SN coupons": SNcoupons,
        "CN coupons": CNcoupons,
        "SN p": SNp,
        "CN p": CNp,
        "SN positive": SNpositive,
        "CN positive": CNpositive
        }
    
    row=json.dump(row,open(savename,"w"))
    
    return row
