import numpy as np
import random as rand

def RDS(net,waves,coupons,p,positive=False):
    """Conducts respondent-driven sampling
    
    Input:
       net:       network, networkx graph
       waves:     maximum number of waves, integer
       coupons:   number of coupons per respondent, integer
       p:         probability of participation, float
       positive:  whether the seed should be HIV-positive, boolean, requires node attribute 'hiv_status' with values of 0 and 1 (positive) for net
    
    Output:
        sampled: list of sampled nodes
    """
    
    #Count number of nodes
    n=np.shape(net)[0]
    #Initialize sample
    sample={}
    #Initialize list of already sampled agents
    sampled=[]
    #Check for HIV positive seed
    if positive:
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
    #Check for waves still to be completed, unsampled nodes, and nodes sampled in previous wave
    while wave<waves and nodes<n and sample[wave]!=[]:
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
    return sampled
