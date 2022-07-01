import os
import subprocess
import pandas as pd

files = subprocess.check_output('find "$PWD" | grep "summary"',shell=True).splitlines()
#filelist = files.decode("utf-8").split("\n")
#filelist = subprocess.run('find "$PWD" | grep "summary"', shell=True,stdout=PIPE).stdout.splitlines()
filelist = [i.decode("utf-8") for i in files]
print(len(files))
print(len(filelist))
master_df = pd.DataFrame()
for f in filelist:
    df = pd.read_csv(f)
    master_df = pd.concat([master_df,df])
    #print(len(master_df.index))
master_df.to_csv("all_summaries.csv",index=False)

