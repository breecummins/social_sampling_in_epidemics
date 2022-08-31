from social_epi import RDS_simulations as rds
import sensitivity_analysis as sa
import os,glob


base = "~/GIT/social_sampling_in_epidemics/simulations/study_params_20220822/"
networks_folder = os.path.expanduser(os.path.join(base,"results_trimmed/JOB643520/"))
rds_config = os.path.expanduser(os.path.join(base,"rds_config.json"))

def v1():
    """Runs all networks."""
    results = sa.run_each(rds_config,networks_folder)
    return results

def v2():
    """Runs one network"""
    full_dir = os.path.join(networks_folder,"TASK1")
    cfile = os.path.join(full_dir,"contact_network.txt")
    tfile = os.path.join(full_dir,"transmission_network.txt")
    tn93file = os.path.join(full_dir,"tn93_distances.csv")
    sfile = glob.glob(os.path.join(full_dir,"social_network*.csv"))[0]
    results = sa.gen_results(cfile,tfile,tn93file,sfile,rds_config)
    return results


if __name__ == "__main__":
    results = v2()
    print(results)






