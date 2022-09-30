import pandas as pd
import numpy as np
import sys,os,ast


# See gemf_README.txt for this information
column_mapper = {0 : "Time", 2 : "Node", 3: "Previous state", 4:"Current state", 6:"# susceptible",7:"# untreated acute",8:"# untreated chronic",11:"# treated acute",12:"# treated chronic"}

# gemf_README.txt maps integer states to FAVITES compartments, i1, i2, a1, a2.
# i1 = untreated acute, i2 = untreated chronic, a1 = treated acute, a2 = treated chronic
compartment_mapper = {1 : "Susceptible", 2 : "Untreated acute", 3 : "Untreated chronic", 6 : "Treated acute", 7 : "Treated chronic"}


def run(dirname):
    '''
    This function makes a new csv that contains the status of each node at the end of the simulation.
    '''
    # The node mapper translates GEMF node indices into the original node indices. The original node indices are stored as strings and so must be converted. The "json" file is not json -- it uses single quotes.
    node_mapper = {k:int(v) for k,v in ast.literal_eval(open(os.path.join(dirname,"gemf2orig.json")).read()).items()}
    oldfilename = os.path.join(dirname,"output.txt")
    filename = os.path.join(dirname,"gemf_compartment_transitions.txt")
    os.system("cp {} {} 2>/dev/null".format(oldfilename,filename))
    df = pd.read_csv(filename,header=None,delim_whitespace=True)
    df = df[[k for k in column_mapper.keys()]]
    df = df.rename(columns=column_mapper)
    df["Current state"] = df["Current state"].map(compartment_mapper)
    df["Previous state"] = df["Previous state"].map(compartment_mapper)
    df["Node"] = df["Node"].map(node_mapper)
    num_swaps = {}
    times2chronic = []
    final_df = pd.DataFrame()
    compartment_transitions = {}
    for node in pd.unique(df["Node"].values):
        temp = df.loc[df["Node"] == node]
        N = len(temp)
        if N in num_swaps:
            num_swaps[N] += 1
        else:
            num_swaps[N] = 1
        T = max(temp["Time"].values)
        if "Susceptible" in temp["Previous state"].values and ("Untreated chronic" in temp["Current state"].values or "Treated chronic" in temp["Current state"].values):
            # print(temp)
            Tm = min(temp["Time"].values)
            temptemp = temp.loc[(temp["Previous state"].isin(["Untreated acute","Treated acute"])) & (temp["Current state"].isin(["Untreated chronic","Treated chronic"]))]
            Tn = min(temptemp["Time"].values)
            times2chronic.append(Tn-Tm)
            # print(Tn-Tm)
        key = " -> ".join(temp["Previous state"].values)
        key = " -> ".join([key,temp["Current state"].values[-1]])
        if key not in compartment_transitions:
            compartment_transitions[key] = 1
        else:
            compartment_transitions[key] += 1
        final_df = pd.concat([final_df,temp.loc[(temp["Node"] == node) & (temp["Time"] == T)]])
    final_df.to_csv(os.path.join(dirname,"final_compartments.csv"),index=False)
    print("Distribution of number of swaps: {}".format(sorted(num_swaps.items())))
    print("Number of infected individuals that underwent a transition: {}".format(len(pd.unique(df["Node"].values))))
    print("Mean and std of time from acute to chronic in years: {} +/- {}".format(np.mean(times2chronic),np.std(times2chronic)))
    print("\nCompartment transition counts:")
    for key,val in sorted(compartment_transitions.items()):
        print("{}: {}".format(key,val))
    print("\n")


def count_compartments(dirname):
    filename = os.path.join(dirname,"final_compartments.csv")
    df = pd.read_csv(filename)
    print("Compartment distribution of (non-isolated) infected individuals at simulation end:")
    print(df["Current state"].value_counts())


if __name__ == "__main__":
    # Need to add for loop over subdirs
    # dirname is location of GEMF results from FAVITES
    dirname = sys.argv[1]
    run(dirname)
    count_compartments(dirname)








