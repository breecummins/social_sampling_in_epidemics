import numpy as np
import networkx as nx
import random as rand
import json

from RDSfunction import RDS
from CountPairsfunction import CountPairs

def Assess(GN,TN,SN,CN,SNwaves,CNwaves,SNcoupons,CNcoupons,SNp,CNp,SNpositive=False,CNpositive=False,savename="rds_params.json"):
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
    
    