# Overview

`social_epi` is a package for generating contact and transmission networks of epidemic spread, generating social networks based on the contact networks, and performing respondent driven sampling (RDS) on the social and contact networks to compare to the ground truth transmission network.

# Dependencies

The following are required pre-installation:

 * Linux or Mac OS operating system
 * Anaconda or Miniconda: https://www.anaconda.com/ or https://docs.conda.io/en/latest/miniconda.html
 * Docker: https://www.docker.com/get-started
 * C tools: make, cmake >= 3.0.0, gcc >= 5.0.0

 The following are dependencies that are installed with `social_epi`.

 * FAVITES: https://github.com/niemasd/FAVITES
    - Resource: https://doi.org/10.1093/bioinformatics/bty921
 * CCMnet_py: https://github.com/ravigoyalgit/CCMnet_py
    - Resource: https://doi.org/10.1017/nws.2014.2
 * TN93: git@github.com:veg/tn93.git
    - Resource: https://doi.org/10.1093/oxfordjournals.molbev.a040023

# Installation

From the commandline, build the conda environment, activate it, and run the installation script.
```bash
$ conda env create -f conda_env.yml
$ source activate social_epi
$ . install.sh
```

 # Usage

 To run FAVITES, create a configuration file (an example is `tests/favites_hiv_test_config.txt`, documentation is in the FAVITES wiki) and do 

 ```bash
$ cd <desired_results_folder>
$ python <path/to/social_sampling_in_epidemics>/scripts/run_favites_docker.py -c <path/to/config>
 ```

 The results will be in a `FAVITES_output` directory. Old results will be overwritten (?)