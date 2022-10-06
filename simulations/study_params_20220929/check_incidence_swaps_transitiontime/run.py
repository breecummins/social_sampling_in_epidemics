import os,json
from social_epi import nx_conversion as nxc


def get_favites(config_file,version,docker_script):
    # args = location of favites config file and name of dir in which to save favites output folder
    os.system("rm -r FAVITES_output_old 2>/dev/null")
    os.system("mv FAVITES_output FAVITES_output_old 2>/dev/null")
    os.system("python {} -u {} -c {}".format(docker_script,version,config_file))
    os.system("gunzip FAVITES_output/error_free_files/transmission_network.txt.gz")


def get_TN(pop=15397,seeds=5588):
    TN,_ = nxc.favitestransmission2nx("FAVITES_output/error_free_files/transmission_network.txt")
    tevents = TN.number_of_edges()
    incidence = tevents/(pop-seeds)
    return incidence


def trigger(contact_config="contact_config.json"):
    cn_config = json.load(open(contact_config))
    print("Finding initial network.")
    initCN = nxc.initial_graph_from_configuration_model(cn_config, cn_config["population"])
    # FIXME: the following line supports hack to mount files in docker/singularity; remove "strip" when favites is updated
    cn_fname = cn_config["G"].strip("/FAVITES_MOUNT/")
    initCN.to_csv(cn_fname,index=False)
    print("Completed.")
    print("Favites starting.",flush=True)
    get_favites("favites_hiv_config.txt","1.2.10","run_favites_docker_with_inputs_implication.py")
    print("Completed.")
    incidence = get_TN()
    print("Incidence = {}".format(incidence))
    os.system("python ../../scripts/modify_status.py FAVITES_output/GEMF_output")
    return incidence


if __name__ == "__main__":
    import numpy as np
    incidence = []
    for _ in range(1):
        incidence.append(trigger())
    statement1 = "Raw incidence: {}".format(["{:.03f}".format(x) for x in incidence])
    print(statement1)
    statement2 = "Incidence mean +/- std: {:.03f} +/- {:.03f}".format(np.mean(incidence),np.std(incidence))
    print(statement2)
    open("summary.txt","w").write("\n".join([statement1,statement2]))

    # Output of run 09/29/2022
    """
    Raw incidence: ['0.017', '0.017', '0.017', '0.015', '0.014', '0.015', '0.015', '0.016', '0.015', '0.014']
    Incidence mean +/- std: 0.016 +/- 0.001
    """

    os.system("python ../../scripts/modify_status.py FAVITES_output/GEMF_output")

    # Output of run 09/29/2022
    """
    Distribution of number of swaps: [(1, 1829), (2, 1422), (3, 651), (4, 144), (5, 15), (6, 6)]
    Number (non-isolated) infected individuals: 4067
    Mean and std of time from acute to chronic in years: 0.09783230769230769 +/- 0.11025268638145162
    Compartment distribution of (non-isolated) infected individuals at simulation end:
    Treated chronic      2470
    Untreated chronic    1583
    Untreated acute        10
    Treated acute           4
    """

    # Output of second run 09/29/2022
    """
    Distribution of number of swaps: [(1, 1851), (2, 1422), (3, 555), (4, 96), (5, 15), (6, 6)]
    Number (non-isolated) infected individuals: 3945
    Mean and std of time from acute to chronic in years: 0.10955319871794873 +/- 0.11525989721382959
    Compartment distribution of (non-isolated) infected individuals at simulation end:
    Treated chronic      2405
    Untreated chronic    1524
    Untreated acute        16
    """


