import sys,os
import subprocess
from social_epi import assign_compartments as acomp
import pandas as pd


def get_final_compartments(master_dir):
    acomp.run_over_multiple_simulations(master_dir)
    acomp.add_compartment_counts_to_summary(master_dir)


def gather_summaries(master_dir,unique_id):
    os.chdir(master_dir)
    os.system("pwd")
    files = subprocess.check_output('find "$PWD" | grep "summary"',shell=True).splitlines()
    filelist = [i.decode("utf-8") for i in files]
    master_df = pd.DataFrame()
    for f in filelist:
        df = pd.read_csv(f)
        master_df = pd.concat([master_df,df])
    master_df.to_csv("all_summaries_{}.csv".format(unique_id),index=False)


if __name__ == "__main__":
    # argument 1 is the directory with multiple tasks from the cluster, e.g.
    # results_trimmed/JOB743857
    # argument is a unique save all summaries file identifier, such as the date

    master_dir = sys.argv[1]
    unique_id = sys.argv[2]
    
    get_final_compartments(master_dir)
    for d in os.listdir(master_dir):
        if os.path.isdir(d):
            acomp.add_compartment_counts_to_summary(os.path.join(master_dir,d))
            acomp.compartment_counts(os.path.join(master_dir,d))
    gather_summaries(master_dir,unique_id)

    
