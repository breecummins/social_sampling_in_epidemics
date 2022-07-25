from social_epi import nx_conversion as nxc
from social_epi import RDS_simulations as rds
import json, os, glob, datetime, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


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


def run_all(base,networks_folder,parentdir,dirnames):
    results_folders = [os.path.expanduser(os.path.join(base,"{}/{}".format(parentdir,dname))) for dname in dirnames]
    for k,rf in enumerate(results_folders):
        starttime = time.time()
        all_results = run_each(os.path.join(rf,"rds_config.json"),networks_folder)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        all_results.to_csv(os.path.join(rf,"all_results_{}.csv".format(timestamp)),index=False)
        print("250 RDS simulations {} complete, Time elapsed: {}".format(k+1,time.time()-starttime))


def make_stats_df(results_dirs,xvals,xlabel):
    column_names = ["param_type","param_val","overlap","mean of props","std of props","mean of raw count","std of raw count"]
    stats_df = pd.DataFrame(columns=column_names)

    def calc_stats(stats_df,df,col,overlap,param):
        counts = df["{} count".format(col)].values
        props = counts/df["{} total".format(col)].values
        stats_df = stats_df.append({"param_type": xlabel,"overlap":overlap, "param_val":param, "mean of props":np.mean(props),"std of props":np.std(props), "mean of raw count":np.mean(counts),"std of raw count":np.std(counts)},ignore_index=True)
        return stats_df

    for dir,param in zip(results_dirs,xvals):
        resfile = glob.glob(os.path.join(dir,"all_results*.csv"))[0]
        df = pd.read_csv(resfile)
        for col,overlap in zip(["SN GN","CN GN","SN TN","CN TN"],["social->genetic","contact->genetic","social->transmission","contact->transmission"]):
            stats_df = calc_stats(stats_df,df,col,overlap,param)
    return stats_df.sort_values(["overlap","param_val"])


def visualize(stats_df,result_type="props"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    for key,grp in stats_df.groupby(["overlap"]):
        grp.plot("param_val", "mean of {}".format(result_type), yerr="std of {}".format(result_type), label=key, ax=ax)
    plt.show()


if __name__ == "__main__":
    # simulations on which to do sensitivity analysis
    base = "~/GIT/social_sampling_in_epidemics/simulations/"
    networks_folder = os.path.expanduser(os.path.join(base,"study_params_20220722/results_trimmed/JOB555814"))

    # # sim 1
    # parentdir = "vary_SN_size_20220722"
    # dirnames = ["size_200","size_400","size_600","size_800","size_1000"]
    # param_vals = [200, 400, 600, 800, 1000]
    # param_type = "Social Sample Size"
    # tag = "sn_samp_size"

    # # sim 2
    # parentdir = "vary_SN_acceptance_20220725"
    # dirnames = ["prob_30","prob_35","prob_40","prob_45","prob_50"]
    # param_vals = [0.3,0.35,0.4,0.45,0.5]
    # param_type = "Social Acceptance Probability"
    # tag = "sn_accept_prob"

    # # sim 3
    # parentdir = "vary_CN_acceptance_20220725"
    # dirnames = ["prob_125","prob_150","prob_175","prob_200","prob_225"]
    # param_vals = [0.125,0.150,0.175,0.200,0.225]
    # param_type = "Sexual Contact Acceptance Probability"
    # tag = "cn_accept_prob"

    # sim 4
    parentdir = "vary_RDS_seeds_20220725"
    dirnames = ["seeds_20","seeds_40","seeds_60","seeds_80","seeds_100"]
    param_vals = [20,40,60,80,100]
    param_type = "Number of RDS Seeds"
    tag = "rds_seeds"

    # run simulations
    run_all(base,networks_folder,parentdir,dirnames)
    # calc stats and plot results
    results_dirs = [os.path.join(parentdir,d) for d in dirnames]
    stats_df = make_stats_df(results_dirs,param_vals,param_type)
    stats_df.to_csv(os.path.join(parentdir,"sensitivity_stats_{}.csv".format(tag)),index=False)
    visualize(stats_df,result_type="props")
    

    


