import os
import subprocess
import pandas as pd

files = subprocess.check_output('find "$PWD" | grep "summary"',shell=True)
filelist = files.decode("utf-8").split("\n")
master_df = pd.DataFrame()
for f in filelist:
    if f:
        df = pd.read_csv(f)
        master_df = pd.concat([master_df,df])
master_df.to_csv("all_summaries.csv",index=False)

