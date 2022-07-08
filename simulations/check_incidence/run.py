import os
from social_epi import nx_conversion as nxc


def get_favites(config_file,version,docker_script):
    # args = location of favites config file and name of dir in which to save favites output folder
    os.system("mv FAVITES_output FAVITES_output_old 2>/dev/null")
    os.system("python {} -u {} -c {}".format(docker_script,version,config_file))
    os.system("gunzip FAVITES_output/error_free_files/transmission_network.txt.gz")


def get_TN(pop=15397,seeds=5588):
    TN,_ = nxc.favitestransmission2nx("FAVITES_output/error_free_files/transmission_network.txt")
    tevents = TN.number_of_edges()
    incidence = tevents/(pop-seeds)
    return incidence


def trigger():
    print("Favites starting.",flush=True)
    get_favites("favites_hiv_config.txt","1.2.10","run_favites_docker_with_inputs_bigbox.py")
    print("Completed.")
    print("Incidence = {}".format(get_TN()))


if __name__ == "__main__":
    trigger()

