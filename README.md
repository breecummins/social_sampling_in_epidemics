# Overview

`social_epi` is a package for generating contact and transmission networks of epidemic spread, generating social networks based on the contact networks, and performing respondent driven sampling (RDS) on the social and contact networks to compare to the ground truth transmission network.

# Dependencies

The following are required pre-installation:

 * Linux or Mac OS operating system
 * Anaconda or Miniconda: https://www.anaconda.com/ or https://docs.conda.io/en/latest/miniconda.html
 * Docker: https://www.docker.com/get-started

 The following are dependencies that are installed with `social_epi`.

 * FAVITES: https://github.com/niemasd/FAVITES
    - Resource: https://doi.org/10.1093/bioinformatics/bty921
 * CCMnet_py: https://github.com/ravigoyalgit/CCMnet_py
    - Resource: https://doi.org/10.1017/nws.2014.2

# Installation

From the commandline, build the conda environment, activate it, and run the installation script.
```bash
$ conda env create -f conda_env.yml
$ source activate social_epi
$ . install.sh
```

 # Usage