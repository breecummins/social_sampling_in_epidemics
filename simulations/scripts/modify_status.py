import pandas as pd
import numpy as np
import sys,os,ast

# See gemf_README.txt for this information
column_mapper = {0 : "Time", 2 : "Node", 3: "Previous state", 4:"Current state", 6:"# susceptible",7:"# untreated acute",8:"# untreated chronic",11:"# treated acute",12:"# treated chronic",13:"# out-of-care"}

# gemf_README.txt maps integer states to FAVITES compartments, i1, i2, a1, a2, a3.
# i1 = untreated acute, i2 = untreated chronic, a1 = treated acute, a2 = treated chronic, a3 = out-of-care
compartment_mapper = {1 : "Susceptible", 2 : "Untreated acute", 3 : "Untreated chronic", 6 : "Treated acute", 7 : "Treated chronic", 8 : "Out-of-care"}


def get_nontransitioned_individuals():
    pass


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
    nodes = pd.unique(df["Node"].values)
    for node in nodes:
        temp = df.loc[df["Node"] == node]
        # N = len(temp)
        # if N in num_swaps:
        #     num_swaps[N] += 1
        # else:
        #     num_swaps[N] = 1
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
    final_df.to_csv(os.path.join(dirname,"final_transitions.csv"),index=False)
    truncated = final_df[["Node","Current state"]]
    
    # add all the (non-isolated) nodes that never underwent transition
    # status.txt has all the initial compartments of the nodes
    sdf = pd.read_csv(os.path.join(dirname,"status.txt"),header=None)
    d = [(k+1,int(v[0])) for k,v in enumerate(sdf.values)]
    compartments = pd.DataFrame(d,columns=["Node","Current state"])
    compartments["Node"] =compartments["Node"].map(node_mapper)
    compartments["Current state"] = compartments["Current state"].map(compartment_mapper)

    # update the initial status with the final status for nodes that underwent transition
    compartments.set_index("Node",inplace=True)
    compartments.update(truncated.set_index("Node"))
    compartments.reset_index(inplace=True)
    compartments.to_csv(os.path.join(dirname,"final_compartments.csv"),index=False)

    # print results
    # print("Distribution of number of swaps: {}".format(sorted(num_swaps.items())))
    print("Number of individuals that underwent a compartment transition: {}".format(len(pd.unique(df["Node"].values))))
    # print("Length of final transitions: {}".format(len(truncated)))
    print("Mean and std of time from acute to chronic in years: {} +/- {}".format(np.mean(times2chronic),np.std(times2chronic)))
    print("\nCompartment transition counts:")
    for key,val in sorted(compartment_transitions.items()):
        print("{}: {}".format(key,val))
    print("\n")


def compartment_counts(dirname):
    filename = os.path.join(dirname,"final_transitions.csv")
    df = pd.read_csv(filename)
    print("Compartment distribution of (non-isolated) individuals at simulation end:")
    temp = df.loc[df["Time"]==max(df["Time"])]
    print("# susceptible: {}".format(temp["# susceptible"].values[0]))
    print("# out-of-care: {}".format(temp["# out-of-care"].values[0]))
    print("# untreated chronic: {}".format(temp["# untreated chronic"].values[0]))
    print("# treated chronic: {}".format(temp["# treated chronic"].values[0]))
    print("# untreated acute: {}".format(temp["# untreated acute"].values[0]))
    print("# treated acute: {}".format(temp["# treated acute"].values[0]))
    filename2 = os.path.join(dirname,"final_compartments.csv")
    df2 = pd.read_csv(filename2)
    print(df2["Current state"]. value_counts())


if __name__ == "__main__":
    # Need to add for loop over subdirs
    # dirname is location of GEMF results from FAVITES
    dirname = sys.argv[1]
    run(dirname)
    compartment_counts(dirname)








