from social_epi import assign_compartments as acomp


if __name__ == "__main__":
    # call from study_params folder
    master_dir = "results_trimmed/JOB739669"
    acomp.run_over_multiple_simulations(master_dir)
