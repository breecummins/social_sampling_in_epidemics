# Overview

`social_epi` is a package for generating contact, transmission, and phylogenetic cluster networks of epidemic spread from parameters, generating social networks based on the contact networks and additional parameters, and performing respondent driven sampling (RDS) on the social and contact networks to compare to the ground truth transmission and phylogenetic cluster networks.

# Dependencies

The following are required pre-installation:

 * Linux or Mac OS operating system with admin privileges (sudo)
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

 ## Generating contact network, transmission network, and genetic sequences

 To run FAVITES, create a configuration file (an example is `tests/favites_hiv_test_config.txt`, documentation is in the FAVITES wiki) and do 

 ```bash
$ cd <desired_results_folder>
$ python <path/to/social_sampling_in_epidemics>/src/tools/run_favites_docker.py -u latest -c <path/to/config>
 ```

 The results will be in a `FAVITES_output` directory. Old results will be overwritten. The files include a contact network file (`contact_network.txt.gz`), a transmission network file (`transmission_network.txt.gz`), and multiple fastq/fasta sequence files. The sequence file to be used in future steps is `sequence_data.fasta.gz`. All files must be unzipped before proceeding to the next steps:

 ```bash
 $ gunzip <file_name>
 ```

 ## Clustering genetic sequences

 To run TN93 and compute pairwise distances, do

 ```bash
 $ tn93 -t 0.05 -o <desired_output_dir>/tn93_distances.dst <path/to/sequence_data.fasta>
 ```
 where `-t` specifies a distance threshold between 0 and 1 (0.05 should be interpreted as 5% sequence divergence), `-o` specifies an output file to save the pairwise distances that are below the threshold, and the last argument is the `fasta` sequence file. There are other options available when working with real as opposed to simulated data.

 To compute the cluster graph from the pairwise distance file, do

 ```bash
 $ cd social_sampling_in_epidemics/src/tools
 $ python tn93_to_clusters.py -i <path/to/tn93_distances.dst> -o <desired_output_dir>/cluster_graph.txt 
 ```

 Optionally, one can pass a `-t` threshold option if it is desired to differ from the one used in the `tn93` command.

 ## Sampling a social network

 Configuration file

 Function call

 ## Simulating Respondent-Driven Sampling

 ## Analyzing outcomes