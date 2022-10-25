import os,json
from social_epi import nx_conversion as nxc
from social_epi import assign_compartments as acomp


def get_favites(config_file,version,docker_script):
    # args = location of favites config file and name of dir in which to save favites output folder
    os.system("rm -r FAVITES_output_old 2>/dev/null")
    os.system("mv FAVITES_output FAVITES_output_old 2>/dev/null")
    os.system("python {} -u {} -c {}".format(docker_script,version,config_file))
    os.system("gunzip FAVITES_output/error_free_files/transmission_network.txt.gz")
    os.system("gunzip FAVITES_output/error_free_files/sequence_data.fasta.gz")
    os.system("tn93 -t {} -o {} {} >/dev/null 2>&1".format(0.015,"FAVITES_output/tn93_distances.csv","FAVITES_output/error_free_files/sequence_data.fasta"))



def get_TN(pop=15397,seeds=5588):
    TN,_ = nxc.favitestransmission2nx("FAVITES_output/error_free_files/transmission_network.txt")
    tevents = TN.number_of_edges()
    incidence = tevents/(pop-seeds)
    return incidence


def trigger(favites_config="favites_hiv_config.txt",contact_config="contact_config.json"):
    cn_config = json.load(open(contact_config))
    print("Finding initial network.")
    initCN = nxc.initial_graph_from_configuration_model(cn_config, cn_config["population"])
    # FIXME: the following line supports hack to mount files in docker/singularity; remove "strip" when favites is updated
    cn_fname = cn_config["G"].strip("/FAVITES_MOUNT/")
    initCN.to_csv(cn_fname,index=False)
    print("Completed.")
    print("Favites starting.",flush=True)
    get_favites(favites_config,"1.2.10","run_favites_docker_with_inputs_implication.py")
    print("Completed.")
    incidence = get_TN()
    print("Incidence = {}".format(incidence))
    acomp.run("FAVITES_output/GEMF_output")
    acomp.compartment_counts("FAVITES_output/GEMF_output")
    return incidence


def trigger_without_ccm(favites_config="favites_hiv_config.txt"):
    print("Favites starting.",flush=True)
    get_favites(favites_config,"1.2.10","run_favites_docker_with_input_contact_network_implication.py")
    print("Completed.")
    incidence = get_TN()
    print("Incidence = {}".format(incidence))
    acomp.run("FAVITES_output/GEMF_output")
    acomp.compartment_counts("FAVITES_output/GEMF_output")
    return incidence


if __name__ == "__main__":
    import numpy as np
    incidence = []
    for _ in range(1):
        incidence.append(trigger_without_ccm("favites_hiv_config_7compartments_contact_network.txt"))
    statement1 = "Raw incidence: {}".format(["{:.03f}".format(x) for x in incidence])
    print(statement1)
    statement2 = "Incidence mean +/- std: {:.03f} +/- {:.03f}".format(np.mean(incidence),np.std(incidence))
    print(statement2)
    open("summary.txt","w").write("\n".join([statement1,statement2]))
