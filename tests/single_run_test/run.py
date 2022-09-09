import os, json
from social_epi import nx_conversion as nxc

cn_config = json.load(open("contact_config.json"))
print("Finding initial network.")
initCN = nxc.initial_graph_from_configuration_model(cn_config, cn_config["population"])
# FIXME: the following line supports hack to mount files in docker/singularity; remove "strip" when favites is updated
cn_fname = os.path.expanduser("~/GIT/social_sampling_in_epidemics/tests/single_run_test/{}".format(cn_config["G"].strip("/FAVITES_MOUNT/"))) 
initCN.to_csv(cn_fname,index=False)
print("Initial network generated.")

os.system("time python run_favites_docker_with_inputs_implication.py -c favites_hiv_config.txt")