import os, datetime,json
from social_epi import nx_conversion as nxc
from social_epi import sampling_social_networks as ssn
from social_epi import RDS_simulations as rds


def get_favites(config_file,results_dir):
    # args = location of favites config file and name of dir in which to save favites output folder
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    os.system("mv FAVITES_output FAVITES_output_old 2>/dev/null")
    os.system("time python src/tools/run_favites_docker.py -u latest -c {}".format(config_file))
    os.system("gunzip FAVITES_output/contact_network.txt.gz")
    os.system("gunzip FAVITES_output/error_free_files/transmission_network.txt.gz")
    os.system("gunzip FAVITES_output/error_free_files/sequence_data.fasta.gz")
    new_results_dir = os.path.abspath(os.path.expanduser(os.path.join(results_dir,"FAVITES_output_{}".format(timestamp))))
    os.system("mv FAVITES_output {}".format(new_results_dir))
    return new_results_dir, timestamp


def get_nets(results_dir,output_dir,threshold=0.015):
    # args : results_dir is favites output dir (e.g. "~/myresults/FAVITES_output_timestamp"), output_dir is where to save tn93 output, threshold is tn93 threshold
    # first get contact and transmission networks
    cnfile = os.path.abspath(os.path.expanduser(os.path.join(results_dir,"contact_network.txt")))
    tnfile = os.path.abspath(os.path.expanduser(os.path.join(results_dir,"error_free_files/transmission_network.txt")))
    CN,TN = nxc.favitescontacttransmission2nx(cnfile,tnfile)
    # next get genetic distance network
    seqfile = os.path.abspath(os.path.expanduser(os.path.join(results_dir,"error_free_files/sequence_data.fasta")))
    distfile = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"tn93_distances.csv")))
    os.system("tn93 -t {} -o {} {} >/dev/null 2>&1".format(threshold,distfile,seqfile))
    GN = nxc.tn93distances2nx(distfile)
    return CN,TN,GN


def get_social_network_sample(CN,TN,config_file,output_dir,timestamp):
    # CN may be a file name or a networkx graph of the contact network
    # If CN is a file name, TN must be specified and is the file name of the transmission network; otherwise TN is None or the empty string
    # config_file is the social network config json
    # output_dir is where to save social network
    # timestamp provides a unique identifier
    SNsavename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"social_network_{}.json".format(timestamp))))
    ONsavename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"overlap_network_{}.json".format(timestamp))))
    SN,ON = ssn.run(config_file,CN,TN)
    SNdf = nxc.nx2pandas(SN)
    SNdf.to_csv(SNsavename,index=False)
    ONdf = nxc.nx2pandas(ON)
    ONdf.to_csv(ONsavename,index=False)
    return SN,ON


def get_rds(GN,TN,SN,CN,config_file,output_dir,timestamp=""):
    savename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"rds_results_{}.json".format(timestamp))))
    config = json.load(open(config_file))
    config["savename"] = savename
    results = rds.Assess(GN,TN,SN,CN,config)
    return results


def chain(contact_config,favites_config,social_config,rds_config,master_results_dir):
    #FIXME: ideally the master_results_dir is passed to contact_initial and the savename 
    # in the contact_config is concatenated with it and inserted into the favites_config.
    # This currently requires an eval(open(favites_config).read()), which I am unwilling to do.
    # So the hack is that the savename for the initial seed contact network is required to be 
    # hard-coded in two config files: contact_config and favites_config. 
    # Yuck. That's a bug generator right there.
    #
    #FIXME Alternative: Write ccm config into template favites config on the fly.
    #
    cn_config = json.load(open(contact_config))
    initCN = nxc.initial_graph_from_configuration_model(cn_config, cn_config["population"])
    initCN.to_csv(cn_config["G"])
    results_dir, timestamp = get_favites(favites_config,master_results_dir)
    CN,TN,GN = get_nets(results_dir,master_results_dir)
    SN = get_social_network_sample(CN,TN,social_config,master_results_dir,timestamp)
    summary = get_rds(GN,TN,SN,CN,rds_config,master_results_dir,timestamp)
    # save configs
    for c in [favites_config,social_config,rds_config]:        
        newfile = os.path.basename(os.path.splitext(c)[0])+"_{}.json".format(timestamp)
        newpath = os.path.abspath(os.path.expanduser(os.path.join(master_results_dir,newfile)))
        os.system("cp {} {}".format(c,newpath))
    return summary


def start_chain(contact_config,favites_config,social_config,master_results_dir="chain_test"):
    print("Finding initial network.")
    _,_ = nxc.contact_initial(contact_config)
    print("Completed.")
    print("Favites starting.")
    results_dir, timestamp = get_favites(favites_config,master_results_dir)
    print("Completed.")
    print("Network retrieval started.")
    CN,TN,_ = get_nets(results_dir,master_results_dir)
    print("Completed.")
    print("Starting social network sampling.")
    SN = get_social_network_sample(CN,TN,social_config,master_results_dir,timestamp)
    print("Completed.")
    

if __name__ == "__main__":
    # cd tests/chain_test/FAVITES_output
    CN = "contact_network.txt"
    TN = "error_free_files/transmission_network.txt"
    config_file="../../../src/configs/sampling_social_networks_config.json"
    SN,ON = ssn.run(config_file,CN,TN)
    print(SN.number_of_nodes())
    print(SN.number_of_edges())


