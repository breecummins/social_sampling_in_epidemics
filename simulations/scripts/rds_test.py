from social_epi import RDS_simulations as rds
import sensitivity_analysis as sa
import os


base = "~/GIT/social_sampling_in_epidemics/simulations/study_params_20220722/"
networks_folder = os.path.expanduser(os.path.join(base,"results_trimmed/JOB555814"))
rds_config = os.path.expanduser(os.path.join(base,"rds_config.json"))

results = sa.run_each(rds_config,networks_folder)



