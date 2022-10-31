import pandas as pd
import os,ast,json,glob

# See gemf_README.txt for this information
column_mapper = {0 : "Time", 2 : "Node", 3: "Previous state", 4:"Current state", 6:"# susceptible",7:"# untreated acute",8:"# untreated chronic", 9: "# out-of-care", 11:"# treated acute",12:"dummy",13: "# treated chronic"}

# gemf_README.txt maps integer states to FAVITES compartments, i1, i2, a1, a2, a3.
# i1 = untreated acute, i2 = untreated chronic, a1 = treated acute, a2 = treated chronic, a3 = out-of-care
compartment_mapper = {1 : "Susceptible", 2 : "Untreated acute", 3 : "Untreated chronic", 4 :"Out-of-care", 6 : "Treated acute", 7 : "dummy", 8 : "Treated chronic"}


def run(dirname):
    '''
    This function makes a new csv that contains the status of each node at the end of the simulation.
    '''
    # The node mapper translates GEMF node indices into the original node indices. The original node indices are stored as strings and so must be converted. The "json" file is not json -- it uses single quotes.
    node_mapper = {k:int(v) for k,v in ast.literal_eval(open(os.path.join(dirname,"gemf2orig.json")).read()).items()}
    # The compartment transitions will have one of two names
    oldfilename = os.path.join(dirname,"output.txt")
    filename = os.path.join(dirname,"gemf_compartment_transitions.txt")
    os.system("cp {} {} 2>/dev/null".format(oldfilename,filename))
    df = pd.read_csv(filename,header=None,delim_whitespace=True)
    # The column mapper gives real names to each column instead of integers
    df = df[[k for k in column_mapper.keys()]]
    df = df.rename(columns=column_mapper)
    # The compartment mapper gives real names to each indexed compartment
    df["Current state"] = df["Current state"].map(compartment_mapper)
    df["Previous state"] = df["Previous state"].map(compartment_mapper)
    # Apply node mapper to translate into original nodes
    df["Node"] = df["Node"].map(node_mapper)
    times2chronic = []
    final_df = pd.DataFrame()
    compartment_transitions = {}
    nodes = pd.unique(df["Node"].values)
    # For each unique node, extract all compartment transitions and compute three things
    for node in nodes:
        temp = df.loc[df["Node"] == node]
        T = max(temp["Time"].values)
        # Compute time from acute to chronic for the individual
        if "Susceptible" in temp["Previous state"].values and ("Untreated chronic" in temp["Current state"].values or "Treated chronic" in temp["Current state"].values):
            Tm = min(temp["Time"].values)
            temptemp = temp.loc[(temp["Previous state"].isin(["Untreated acute","Treated acute"])) & (temp["Current state"].isin(["Untreated chronic","Treated chronic","dummy"]))]
            Tn = min(temptemp["Time"].values)
            times2chronic.append(Tn-Tm)
        # Record the sequence of compartment swaps for the individual
        key = " -> ".join(temp["Previous state"].values)
        key = " -> ".join([key,temp["Current state"].values[-1]])
        if key not in compartment_transitions:
            compartment_transitions[key] = 1
        else:
            compartment_transitions[key] += 1
        # Get the last compartment. There can be more than one compartment at the latest time because of the infinite transition rate from dummy (a2) compartment to treated chronic (a3) compartment. 
        # So remove dummy current status.
        newrow = temp.loc[(temp["Node"] == node) & (temp["Time"] == T) & (temp["Current state"] != "dummy")]
        final_df = pd.concat([final_df,newrow])
        if newrow.empty:
            changedrow = temp.loc[(temp["Node"] == node) & (temp["Time"] == T)]
            if changedrow["Current state"].values[0] == "dummy":
                changedrow["Current state"] = "Treated chronic"
                final_df = pd.concat([final_df,changedrow])
            else:
                raise ValueError("Unrecognized compartment: {}".format(changedrow["Current state"]))
    final_df.to_csv(os.path.join(dirname,"final_transitions.csv"),index=False)
    truncated = final_df[["Node","Current state"]]
    
    # add all the (non-isolated) nodes that never underwent transition
    # status.txt has all the initial compartments of the nodes, but may have been renamed
    oldfilename = os.path.join(dirname,"status.txt")
    filename = os.path.join(dirname,"gemf_initial_compartments.txt")
    os.system("cp {} {} 2>/dev/null".format(oldfilename,filename))
    sdf = pd.read_csv(os.path.join(dirname,"gemf_initial_compartments.txt"),header=None)
    d = [(k+1,int(v[0])) for k,v in enumerate(sdf.values)]
    compartments = pd.DataFrame(d,columns=["Node","Current state"])
    compartments["Node"] =compartments["Node"].map(node_mapper)
    compartments["Current state"] = compartments["Current state"].map(compartment_mapper)
    
    # update the initial status with the final status for nodes that underwent transition
    compartments.set_index("Node",inplace=True)
    compartments.update(truncated.set_index("Node"))
    compartments.reset_index(inplace=True)
    compartments.to_csv(os.path.join(dirname,"final_compartments.csv"),index=False)
    json.dump(compartment_transitions,open(os.path.join(dirname,"compartment_transitions.json"),"w"))

    # # print results
    # # print("Distribution of number of swaps: {}".format(sorted(num_swaps.items())))
    # print("Number of individuals that underwent a compartment transition: {}".format(len(pd.unique(df["Node"].values))))
    # # print("Length of final transitions: {}".format(len(truncated)))
    # print("Mean and std of time from acute to chronic in years: {} +/- {}".format(np.mean(times2chronic),np.std(times2chronic)))
    # print("\nCompartment transition counts:")
    # for key,val in sorted(compartment_transitions.items()):
    #     print("{}: {}".format(key,val))
    # print("\n")


def add_compartment_counts_to_summary(dirname):
    sumfile = glob.glob(os.path.join(dirname,"summary*.csv"))[0]
    df = pd.read_csv(sumfile)
    # df = df.drop(["SN Susceptible","SN Untreated acute","SN Treated acute","SN Untreated chronic","SN Treated chronic","CN Susceptible","CN Untreated acute","CN Treated acute","CN Untreated chronic","CN Treated chronic", "SN HIV+ Isolated","CN HIV+ Isolated"],axis=1)
    fcfile = os.path.join(dirname,"final_compartments.csv")
    comp_df = pd.read_csv(fcfile)
    social_sample = ast.literal_eval(df["SN sampled"].values[0])
    contact_sample = ast.literal_eval(df["CN sampled"].values[0])
    social_seed = ast.literal_eval(df["SN seed"].values[0])
    contact_seed = ast.literal_eval(df["CN seed"].values[0])
    new_social_nodes = set(social_sample).difference(set(social_seed))
    new_contact_nodes = set(contact_sample).difference(set(contact_seed))
    social_df = comp_df[comp_df["Node"].isin(new_social_nodes)]
    contact_df = comp_df[comp_df["Node"].isin(new_contact_nodes)]
    all_comps = list(compartment_mapper.values())
    all_comps.remove("dummy")
    social_comps=social_df["Current state"].value_counts().to_dict()
    contact_comps = contact_df["Current state"].value_counts().to_dict()
    for key in sorted(all_comps):
        df["SN "+key] = [0] if key not in social_comps else [social_comps[key]]
        df["CN "+key] = [0] if key not in contact_comps else [contact_comps[key]]
    df["SN HIV+ Isolated"] = [df["SN HIV+"].values[0] - df["SN Out-of-care"].values[0] - df["SN Untreated acute"].values[0]- df["SN Treated acute"].values[0]- df["SN Untreated chronic"].values[0]- df["SN Treated chronic"].values[0]]
    df["CN HIV+ Isolated"] = [df["CN HIV+"].values[0] - df["CN Out-of-care"].values[0] - df["CN Untreated acute"].values[0]- df["CN Treated acute"].values[0]- df["CN Untreated chronic"].values[0]- df["CN Treated chronic"].values[0]]
    df.to_csv(sumfile,index=False)    


def compartment_counts(dirname):
    filename2 = os.path.join(dirname,"final_compartments.csv")
    df2 = pd.read_csv(filename2)
    print(df2["Current state"]. value_counts())


def run_over_multiple_simulations(master_dir):
    for d in os.listdir(master_dir):
        if os.path.isdir(os.path.join(master_dir,d)):
            run(os.path.join(master_dir,d))


if __name__ == "__main__":
    import sys
    # dirname is location of GEMF results from FAVITES
    dirname = sys.argv[1]
    run(dirname)
    # compartment_counts(dirname)

    # master_dir = "results_trimmed/JOB739669/"
    # for d in os.listdir(master_dir):
    #     add_compartment_counts_to_summary(os.path.join(master_dir,d))
    #     compartment_counts(os.path.join(master_dir,d))








