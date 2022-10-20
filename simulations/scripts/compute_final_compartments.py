from social_epi import assign_compartments as acomp
import pandas as pd
import ast

def get_final_compartments(master_dir):
    acomp.run_over_multiple_simulations(master_dir)


def sampled_compartment_counts(summary_file,final_compartment_file):
    df = pd.read_csv(summary_file)
    comp_df = pd.read_csv(final_compartment_file)
    social_sample = ast.literal_eval(df["SN sampled"].values[0])
    contact_sample = ast.literal_eval(df["CN sampled"].values[0])
    social_df = comp_df[comp_df["Node"].isin(social_sample)]
    contact_df = comp_df[comp_df["Node"].isin(contact_sample)]
    social_compartments = social_df["Current state"].value_counts().to_dict()
    contact_compartments = contact_df["Current state"].value_counts().to_dict()
    return social_compartments, contact_compartments


if __name__ == "__main__":
    # # call from study_params folder
    # master_dir = "results_trimmed/JOB739669"
    # get_final_compartments(master_dir)

    social,contact=sampled_compartment_counts("results_trimmed/JOB739669/TASK1/summary_20221017102748.csv","results_trimmed/JOB739669/TASK1/final_compartments.csv")
    print("Social")
    print(social)
    print('\n')
    print("Contact")
    print(contact)
