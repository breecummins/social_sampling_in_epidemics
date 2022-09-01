import os,glob,json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from social_epi import RDS_simulations as rds
from social_epi import nx_conversion as nxc


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


def make_stats_df(results_df):
    column_names = ["overlap","mean of props","std of props","mean of raw count","std of raw count"]
    stats_df = pd.DataFrame(columns=column_names)

    def calc_stats(stats_df,df,numerator_col,denominator_col,overlap):
        counts = df["{}".format(numerator_col)].values
        props = counts/df["{}".format(denominator_col)].values
        stats_df = stats_df.append({"overlap":overlap, "mean of props":np.mean(props),"std of props":np.std(props), "mean of raw count":np.mean(counts),"std of raw count":np.std(counts)},ignore_index=True)
        return stats_df

    # for (numerator_col,denominator_col),overlap in zip([("SN GN count","SN GN total"),("CN GN count","CN GN total"),("SN TN count","SN TN total"),("CN TN count","CN TN total"),("SN HIV+","SN sampled"),("CN HIV+","CN sampled")],["social->genetic","contact->genetic","social->transmission","contact->transmission", "social HIV+", "contact HIV+"]):
    for (numerator_col,denominator_col),overlap in zip([("SN HIV+","SN sampled"),("CN HIV+","CN sampled")],["social HIV+", "contact HIV+"]):
        stats_df = calc_stats(stats_df,results_df,numerator_col,denominator_col,overlap)
    return stats_df.sort_values(["overlap"])


if __name__ == "__main__":
    networks_folder =  os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/study_params_20220822/results_trimmed/JOB643520")
    rds_config = os.path.expanduser("~/GIT/social_sampling_in_epidemics/simulations/study_params_202200901/rds_config.json")
    results = run_each(rds_config,networks_folder)
    results.to_csv("all_summaries_20220901.csv",index=False)
    stats_df = make_stats_df(results)
    print(stats_df)




