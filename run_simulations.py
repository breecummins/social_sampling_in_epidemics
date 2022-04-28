import os, datetime,json
from social_epi import nx_conversion as nxc
from social_epi import sampling_social_networks as ssn
from social_epi import RDS_simulations as rds


def get_favites(config_file,results_dir):
    # args = location of favites config file and name of dir in which to save favites output folder
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    os.system("time python src/tools/run_favites_docker.py -u latest -c {}".format(config_file))
    os.system("gunzip FAVITES_output/contact_network.txt.gz")
    os.system("gunzip FAVITES_output/error_free_files/transmission_network.txt.gz")
    os.system("gunzip FAVITES_output/error_free_files/sequence_data.fasta.gz")
    new_results_dir = os.path.abspath(os.path.expanduser(os.path.join(results_dir,"FAVITES_output_{}".format(results_dir,timestamp))))
    os.system("mv FAVITES_output {}".format(new_results_dir))
    os.system("rm -r FAVITES_output")
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
    os.system("tn93 -t {} -o {} {}".format(threshold,distfile,seqfile))
    GN = nxc.tn93distances2nx(distfile)
    return CN,TN,GN


def get_social_network_sample(CN,TN,config_file,output_dir,timestamp=None):
    # CN and TN may be file names or networkx graphs
    # output_dir is where to save social network
    savename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"social_network_{}.json".format(timestamp))))
    SN = ssn.run(CN,TN,config_file,savename)
    return SN


def get_rds(GN,TN,SN,CN,config_file,output_dir,timestamp=None):
    savename = os.path.abspath(os.path.expanduser(os.path.join(output_dir,"rds_results_{}.json".format(timestamp))))
    config = json.load(open(config_file))
    config["savename"] = savename
    results = rds.Assess(GN,TN,SN,CN,config)
    return results


def chain(favites_config,social_config,rds_config,master_results_dir):
    results_dir, timestamp = get_favites(favites_config,master_results_dir)
    CN,TN,GN = get_nets(results_dir,master_results_dir)
    SN = get_social_network_sample(CN,TN,social_config,master_results_dir,timestamp)
    summary = get_rds(GN,TN,SN,CN,rds_config,master_results_dir,timestamp)
    return summary



