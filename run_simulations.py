import os, datetime,json
from social_epi import nx_conversion as nxc
from social_epi import sampling_social_networks as ssn
from social_epi import RDS_simulations as rds


def get_favites(config_file,results_dir,version,docker_script):
    # args = location of favites config file and name of dir in which to save favites output folder
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    os.system("mv FAVITES_output FAVITES_output_old 2>/dev/null")
    os.system("python {} -u {} -c {}".format(docker_script,version,config_file))
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
    GN = nxc.tn93distances2nx(tnfile,distfile)
    return CN,TN,GN


def get_social_network_sample(CN,TN,config_file,output_dir,timestamp):
    # CN may be a file name or a networkx graph of the contact network
    # If CN is a file name, TN must be specified and is the file name of the transmission network; otherwise TN is None or the empty string
    # config_file is the social network config json
    # output_dir is where to save social network
    # timestamp provides a unique identifier
    SNsavename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"social_network_{}.csv".format(timestamp))))
    ONsavename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"overlap_network_{}.csv".format(timestamp))))
    config = json.load(open(config_file))
    fname = os.path.splitext(os.path.basename(config["savename_initial"]))[0]+"_{}.csv".format(timestamp)
    spath = os.path.abspath(os.path.expanduser(os.path.join(output_dir,fname)))
    config["savename_initial"] = spath
    gname = os.path.splitext(os.path.basename(config["savename_ccm_config"]))[0]+"_{}.json".format(timestamp)
    cpath = os.path.abspath(os.path.expanduser(os.path.join(output_dir,gname)))
    config["savename_ccm_config"] = cpath
    SN,ON = ssn.run(config,CN,TN)
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


def chain(contact_config,favites_config,social_config,rds_config,master_results_dir,favites_version="latest",docker_script="src/tools/run_favites_docker.py"):
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
    print("Finding initial network.")
    initCN = nxc.initial_graph_from_configuration_model(cn_config, cn_config["population"])
    # FIXME: the following line supports hack to mount files in docker/singularity; remove "strip" when favites is updated
    cn_fname = os.path.abspath(os.path.expanduser(os.path.join(master_results_dir,cn_config["G"].strip("/FAVITES_MOUNT/")))) 
    initCN.to_csv(cn_fname,index=False)
    ###############
    print("Completed.")
    print("Favites starting.")
    results_dir, timestamp = get_favites(favites_config,master_results_dir,favites_version,docker_script)
    print("Completed.")
    print("Network retrieval started.")
    CN,TN,GN = get_nets(results_dir,master_results_dir)
    print("Completed.")
    print("Starting social network sampling.")
    SN,_ = get_social_network_sample(CN,TN,social_config,master_results_dir,timestamp)
    print("Completed.")
    print("Starting RDS simulations.")
    summary = get_rds(GN,TN,SN,CN,rds_config,master_results_dir,timestamp)
    print("Completed.")
    print("Saving results.")
    summaryfname = "summary_{}.csv".format(timestamp)
    summarypath = os.path.abspath(os.path.expanduser(os.path.join(master_results_dir,summaryfname)))
    summary.to_csv(summarypath,index=False)
    # save configs
    for c in [favites_config,social_config,rds_config]:        
        newfile = os.path.basename(os.path.splitext(c)[0])+"_{}.json".format(timestamp)
        newpath = os.path.abspath(os.path.expanduser(os.path.join(master_results_dir,newfile)))
        os.system("cp {} {}".format(c,newpath))
    # # bundle into dir
    # all_dir = os.path.abspath(os.path.expanduser(os.path.join(master_results_dir,"all_output")))
    # os.mkdir(all_dir)
    # os.system("ls ")
    # os.system("mv *{}* {}".format(timestamp,all_dir))
    # os.system("mv {} {}".format(all_dir,all_dir+"_{}".format(timestamp)))
    return summary


if __name__ == "__main__":
    import sys

    '''
    Usage: 
    
    python run_simulations.py <contact_config.json> <favites_config.txt> <social_config.json> <rds_config.json> <results_dir> <favites_version> <path/to/docker-singularity-script>

    favites_version is optional and defaults to "latest".
    path/to/docker is optional and defaults to "src/tools/run_favites_docker.py"
    
    '''

    cc = sys.argv[1]
    fc = sys.argv[2]
    sc = sys.argv[3]
    rc = sys.argv[4]
    rdir = sys.argv[5]
    if len(sys.argv) >7:
        summary = chain(cc,fc,sc,rc,rdir, favites_version=sys.argv[6],docker_script=sys.argv[7])  
    elif len(sys.argv) >6:
        summary = chain(cc,fc,sc,rc,rdir, favites_version=sys.argv[6])  
    else:
        summary = chain(cc,fc,sc,rc,rdir)

    print(summary)



    # # cd tests/chain_test/FAVITES_output
    # CN = "contact_network.txt"
    # TN = "error_free_files/transmission_network.txt"
    # config_file="../../../src/configs/sampling_social_networks_config.json"
    # SN,ON = ssn.run(config_file,CN,TN)
    # print(SN.number_of_nodes())
    # print(SN.number_of_edges())

    # # cd tests/chain_test/FAVITES_output
    # CN,TN,GN = get_nets("","",threshold=0.015)
    # CNdf = nxc.nx2pandas(CN)
    # CNdf.to_csv("contact_network.csv",index=False)
    # TNdf = nxc.nx2pandas(TN)
    # TNdf.to_csv("transmission_network.csv",index=False)
    # GNdf = nxc.nx2pandas(GN)
    # GNdf.to_csv("genetic_cluster_network.csv",index=False)

    # # for Kara
    # CN,TN = nxc.favitescontacttransmission2nx("contact_network.txt","transmission_network.txt")
    # os.system("tn93 -t {} -o {} {} >/dev/null 2>&1".format(0.015,"tn93_distances.csv","sequence_data.fasta"))
    # GN = nxc.tn93distances2nx("transmission_network.txt","tn93_distances.csv")
    # SN,_ = ssn.run("sampling_social_networks_config.json",CN)
    # param_dict = json.load(open("rds_config.json"))
    # summary = rds.Assess(GN,TN,SN,CN,param_dict)
    # summary.to_csv("summary.csv",index=False)
    


