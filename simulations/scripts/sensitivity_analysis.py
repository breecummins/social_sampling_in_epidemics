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


def run_all(networks_folder,parentdir,dirnames,params):
    results_folders = [os.path.expanduser(os.path.join(parentdir,"{}".format(dname))) for dname in dirnames]
    for k,rf in zip(params,results_folders):
        starttime = time.time()
        all_results = run_each(os.path.join(rf,"rds_config.json"),networks_folder)
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        all_results.to_csv(os.path.join(rf,"all_results_{}.csv".format(timestamp)),index=False)
        print("250 RDS simulations for param {} complete, Time elapsed: {}".format(k,time.time()-starttime))


def make_stats_df(results_dirs,xvals,xlabel):
    column_names = ["param_type","param_val","overlap","mean of props","std of props","mean of raw count","std of raw count"]
    stats_df = pd.DataFrame(columns=column_names)

    def calc_stats(stats_df,df,col,overlap,param):
        counts = df["{} count".format(col)].values
        props = counts/df["{} total".format(col)].values
        stats_df = stats_df.append({"param_type": xlabel,"overlap":overlap, "param_val":param, "mean of props":np.mean(props),"std of props":np.std(props), "mean of raw count":np.mean(counts),"std of raw count":np.std(counts)},ignore_index=True)
        return stats_df

    for dir,param in zip(results_dirs,xvals):
        print(os.path.isdir(dir))
        print((os.path.join(dir,"all_results*.csv")))
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


def main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False):
    if not load:
        print("Working on {}".format(parentdir))
        run_all(networks_folder,parentdir,dirnames,paramvals)
        # calc stats and plot results
        results_dirs = [os.path.join(parentdir,d) for d in dirnames]
        stats_df = make_stats_df(results_dirs,paramvals,param_type)
        stats_df.to_csv(os.path.join(parentdir,"sensitivity_stats_{}.csv".format(tag)),index=False)
    else:
        stats_df=pd.read_csv(os.path.join(parentdir,"sensitivity_stats_{}.csv".format(tag)))
    visualize(stats_df,result_type="props")


def sn_size(base,networks_folder):
    parentdir = os.path.join(base,"sensitivity_analysis_20220825/vary_SN_size_20220825")
    param_type = "Social Sample Size"
    tag = "sn_samp_size"
    paramvals = [200,300,400,500,600,650,700,750,800,850,900,950,1000]
    dirnames =  ["size_200","size_300","size_400","size_500","size_600","size_650","size_700","size_750","size_800","size_850","size_900","size_950","size_1000"]
    main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False)


def sn_acceptance(base,networks_folder):
    parentdir = os.path.join(base,"sensitivity_analysis_20220825/vary_SN_acceptance_20220829")
    dirnames = ["prob_30","prob_35","prob_40","prob_45","prob_50"]
    paramvals = [0.3,0.35,0.4,0.45,0.5]
    param_type = "Social Acceptance Probability"
    tag = "sn_accept_prob"
    main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False)


def cn_acceptance(base,networks_folder):
    parentdir = os.path.join(base,"sensitivity_analysis_20220825/vary_CN_acceptance_20220829")
    dirnames = ["prob_125","prob_150","prob_175","prob_200","prob_225"]
    paramvals = [0.125,0.150,0.175,0.200,0.225]
    param_type = "Sexual Contact Acceptance Probability"
    tag = "cn_accept_prob"
    main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False)


def rds_seeds(base, networks_folder):
    parentdir = os.path.join(base,"sensitivity_analysis_20220825/vary_rds_seeds_20220825")
    dirnames = ["seeds_10","seeds_20","seeds_30","seeds_40","seeds_50","seeds_60","seeds_70","seeds_80","seeds_90","seeds_100","seeds_110","seeds_120","seeds_130","seeds_140","seeds_150","seeds_200","seeds_300","seeds_400","seeds_500","seeds_600"]
    paramvals = [10,20,30,40,50,60,70,80,90,100,110, 120, 130, 140, 150,200,300,400,500,600]
    param_type = "Number of RDS Seeds"
    tag = "rds_seeds"
    main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False)


def rds_seeds_hivpos(base, networks_folder):
    parentdir = os.path.join(base,"sensitivity_analysis_20220825/vary_rds_seeds_hivpos_20220826")
    dirnames = ["seeds_10","seeds_20","seeds_30","seeds_40","seeds_50","seeds_60","seeds_70","seeds_80","seeds_90","seeds_100","seeds_110","seeds_120","seeds_130","seeds_140","seeds_150","seeds_200","seeds_300","seeds_400","seeds_500","seeds_600"]
    paramvals = [10,20,30,40,50,60,70,80,90,100,110, 120, 130, 140, 150,200,300,400,500,600]
    param_type = "Number of HIV+ RDS Seeds"
    tag = "rds_seeds_hivpos"
    main(networks_folder,parentdir,dirnames,paramvals,param_type,tag,load=False)



if __name__ == "__main__":
    # simulations on which to do sensitivity analysis
    base = os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/")
    networks_folder = os.path.join(base,"study_params_20220822/results_trimmed/JOB643520")
    cn_acceptance(base,networks_folder)

    
    

    


