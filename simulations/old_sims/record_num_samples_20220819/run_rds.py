from social_epi import nx_conversion as nxc
from social_epi import RDS_simulations as rds
import json, os, glob, datetime
import pandas as pd


def gen_results(contacttxt,transmissiontxt,tn93dists,socialcsv,rds_config):
    gn,tn,sn,cn=nxc.reinflate_networks(contacttxt,transmissiontxt,tn93dists,socialcsv)
    rds_param_dict = json.load(open(rds_config))
    return rds.Assess(gn,tn,sn,cn,rds_param_dict)


def run(rds_config,networks_folder):
    all_results = pd.DataFrame()
    for dir in os.listdir(networks_folder):
        full_dir = os.path.join(networks_folder,dir)
        cfile = os.path.join(full_dir,"contact_network.txt")
        tfile = os.path.join(full_dir,"transmission_network.txt")
        tn93file = os.path.join(full_dir,"tn93_distances.csv")
        sfile = glob.glob(os.path.join(full_dir,"social_network*.csv"))[0]
        results = gen_results(cfile,tfile,tn93file,sfile,rds_config)
        all_results = pd.concat([all_results,results])    
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    all_results.to_csv("all_results_{}.csv".format(timestamp),index=False)


if __name__ == "__main__":
    # simulations on which to do sensitivity analysis
    base = "~/GIT/social_sampling_in_epidemics/simulations/"
    networks_folder = os.path.expanduser(os.path.join(base,"study_params_20220722/results_trimmed/JOB555814"))
    run("rds_config.json",networks_folder)

