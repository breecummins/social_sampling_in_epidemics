import ast,os,json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def compute_incidence(dirname, time_in_years, total_pop, num_seeds):
    '''
    Computes the proportion of susceptible individuals that are infected each year of the simulation.
    
    param: dirname = directory containing FAVITES files gemf2orig.json, gemf_compartment_transitions.txt, and gemf_initial_compartments.txt. 
    param: time_in_years = integer representing the (floor of the) number of years that the simulation was run 

    returns: a list with the number of new infections each year and the remaining population of susceptible individuals
    '''

    # The node mapper translates GEMF node indices into the original node indices. The original node indices are stored as strings and so must be converted. The "json" file is not json -- it uses single quotes.
    g2o = os.path.join(dirname,"gemf2orig.json")
    if os.path.exists(g2o):
        node_mapper = {k:int(v) for k,v in ast.literal_eval(open(g2o).read()).items()}
    else:
        print("File gemf2orig.json does not exist in {}.".format(dirname))
        return []

    # See gemf_README.txt for this information
    column_mapper = {0 : "Time", 3: "Previous state", 4:"Current state", 6:"# susceptible"}

    # The compartment transitions will have one of two names
    oldfilename = os.path.join(dirname,"output.txt")
    filename = os.path.join(dirname,"gemf_compartment_transitions.txt")
    os.system("cp {} {} 2>/dev/null".format(oldfilename,filename))
    df = pd.read_csv(filename,header=None,delim_whitespace=True)

    # Keep the columns of interest
    # The column mapper gives real names to each column instead of integers
    df = df[[k for k in column_mapper.keys()]]
    df = df.rename(columns=column_mapper)

    # get initial susceptible population
    ip = open(os.path.join(dirname,"gemf_initial_compartments.txt")).readlines()
    sim_pop = len(ip)
    init_sus_pop_sim = ip.count("1\n") + ip.count("0\n")
    disconnected_nodes = total_pop - sim_pop
    disconnected_infected = num_seeds - (sim_pop - init_sus_pop_sim) 
    disconnected_susceptible = disconnected_nodes - disconnected_infected
    init_sus_pop = init_sus_pop_sim + disconnected_susceptible
    sus_pop = [init_sus_pop]

    # get susceptible populations and transitions for each year
    new_infections = []
    for k in range(1,time_in_years+1):
        # extract yearly data
        rows = df[(df["Time"] > k-1) & (df["Time"] <= k)]
        # Transitions from susceptible to infected
        new_infections.append(sum((rows["Previous state"] == 1) & (rows["Current state"] == 2)))
        # Susceptible population at the end of the year
        M = rows["Time"].astype(float).max()
        row = rows[rows["Time"] == M]
        sus_pop.append(int(row["# susceptible"].max())+ disconnected_susceptible)
     
    # compute yearly incidences
    incidences = [i/j for i,j in zip(new_infections,sus_pop[:-1])]
    return incidences


def compute_stats(incidences,savename):
    # compute year-by-year stats
    means, stds = [],[]
    for r in zip(*incidences):
        r = list(r)
        means.append(np.mean(r))
        stds.append(np.std(r))

    # save files
    json.dump([means,stds],open(os.path.expanduser(savename),"w"))
    return means, stds


def plot_stats(means,stds,sim_years,saveplt):
    x = range(1,sim_years+1)
    plt.figure()
    plt.xlabel('Years')
    plt.ylabel('Incidence rates')
    plt.grid(True, axis='y')
    plt.bar(x, means, yerr=stds, capsize=8, alpha=0.6, color='b')
    plt.savefig(saveplt)
    plt.show()


if __name__ == "__main__":

    # from configuration file
    total_pop = 15397 
    num_seeds = 5588
    sim_years = 6

    # get incidences from 250 simulations
    incidences = []
    for k in range(1,251):
        print("TASK{}".format(k))
        fname = "study_params_20220929/results_trimmed_end/JOB758832/TASK{}".format(k)
        if os.path.exists(fname):
            i = compute_incidence(fname,sim_years,total_pop,num_seeds)
            if len(i) > 0:
                incidences.append(i)

    savename = "~/Desktop/incidences_stats.json"
    compute_stats(incidences,savename)

    means,stds = json.load(open(os.path.expanduser(savename)))
    saveplt = "~/Desktop/incidences_stats.pdf"
    plot_stats(means,stds,sim_years,os.path.expanduser(saveplt))

    

    


