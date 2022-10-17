import sys
import subprocess
import pandas as pd

# cd results on cluster (tempest)
# argument is unique save name identifier, e.g. the date

files = subprocess.check_output('find "$PWD" | grep "summary"',shell=True).splitlines()
filelist = [i.decode("utf-8") for i in files]
master_df = pd.DataFrame()
for f in filelist:
    df = pd.read_csv(f)
    master_df = pd.concat([master_df,df])
master_df.to_csv("all_summaries_{}.csv".format(sys.argv[1]),index=False)

