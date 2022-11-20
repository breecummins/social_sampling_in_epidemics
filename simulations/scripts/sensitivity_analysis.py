from social_epi import nx_conversion as nxc
from social_epi import RDS_simulations as rds
import json, os, glob, datetime, time
import pandas as pd


def gen_results(contacttxt,transmissiontxt,tn93dists,socialcsv,rds_config):
    gn,tn,sn,cn=nxc.reinflate_networks(contacttxt,transmissiontxt,tn93dists,socialcsv)
    rds_param_dict = json.load(open(rds_config))
    return rds.Assess(gn,tn,sn,cn,rds_param_dict)


def run_each(rds_config,networks_folder):
    all_results = pd.DataFrame()
    for dir in os.listdir(networks_folder):
        full_dir = os.path.join(networks_folder,dir)
        cfile = os.path.join(full_dir,"contact_network.txt")
        tfile = os.path.join(full_dir,"transmission_network.txt")
        tn93file = os.path.join(full_dir,"tn93_distances.csv")
        sfile = glob.glob(os.path.join(full_dir,"social_network*.csv"))[0]
        results = gen_results(cfile,tfile,tn93file,sfile,rds_config)
        all_results = pd.concat([all_results,results])    
    return all_results


def run_all(networks_folder,sensitivity_folders):
    for sf in sensitivity_folders:
        starttime = time.time()
        all_results = run_each(os.path.join(sf,"rds_config.json"),networks_folder)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        all_results.to_csv(os.path.join(sf,"all_results_{}.csv".format(timestamp)),index=False)
        print("250 RDS simulations for folder {} complete, Time elapsed: {}".format(sf,time.time()-starttime))


if __name__ == "__main__":
    import sys
    # first arg is location of the already generated networks on which to re-perform RDS
    # all subsequent arguments are the folders that each contain an rds_config.json to be run on the networks in networks_folder 
    # Example: 
    # python sensitivity_analysis.py ~/GIT/social_sampling_in_epidemics/simulations/study_params_20220929/results_trimmed_end/JOB758832 ~/GIT/social_sampling_in_epidemics/simulations/study_params_20220929/sensitivity_analysis_acceptance/acceptance00 ~/GIT/social_sampling_in_epidemics/simulations/study_params_20220929/sensitivity_analysis_acceptance/acceptance02
    # etc
    
    networks_folder = sys.argv[1]
    sensitivity_folders = sys.argv[2:]
    run_all(networks_folder,sensitivity_folders)

    


