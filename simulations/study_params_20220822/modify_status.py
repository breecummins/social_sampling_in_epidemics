from fileinput import filename
import pandas as pd
import numpy as np
import sys,os


# column_mapper = {0 : "Time", 2 : "Node", 3: "Previous state", 4:"Current state", "6":"# susceptible",7:"# untreated acute",8:"# untreated chronic",11:"# treated acute",12:"# treated chronic"}

column_mapper = {0:"Status"}

compartment_mapper = {1 : "Susceptible", 2 : "Untreated acute", 3 : "Untreated chronic", 6 : "Treated acute", 7 : "Treated chronic"}

def run(dirname):
    filename = os.path.join(dirname,"compartment_status.txt")
    df = pd.read_csv(filename,header=None)
    df = df.rename(columns=column_mapper)
    df["Node"] = np.arange(len(df))
    df["Status"] = df["Status"].map(compartment_mapper)
    df.to_csv(filename,index=False)


if __name__ == "__main__":
    dirname = sys.argv[1]
    run(dirname)








