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

 To run FAVITES, create a configuration file (an example is `tests/favites_hiv_test_config.txt`, **documentation needed**) and do 

 ```bash
$ cd <desired_results_folder>
$ python <path/to/social_sampling_in_epidemics>/src/tools/run_favites_docker.py -u latest -c <path/to/config>
 ```

 The results will be in a `FAVITES_output` directory. Old results will be overwritten. The files include a contact network file (`contact_network.txt.gz`), a transmission network file (`transmission_network.txt.gz`), and multiple fastq/fasta sequence files. The sequence file to be used in future steps is `sequence_data.fasta.gz`. Unzip before proceeding to the next steps:

 ```bash
 $ gunzip <path/to/sequence_data.fasta.gz>
 ```

 ## Computing distances between genetic sequences

 To run TN93 and compute pairwise distances, do

 ```bash
 $ tn93 -t 0.05 -o <desired_output_dir>/tn93_distances.csv <path/to/sequence_data.fasta>
 ```
 where `-t` specifies a distance threshold between 0 and 1 (0.05 should be interpreted as 5% sequence divergence), `-o` specifies an output file to save the pairwise distances that are below the threshold in csv format, and the last argument is the `fasta` sequence file. There are other options available when working with real as opposed to simulated data.


 ## Sampling a social network

 The function `sampling_social_networks.py` accepts a contact network and produces a single random social network based on features of the contact network. In particular, a random subgraph of the contact network is held fixed and a CCM network sample is drawn according to the degree distribution of the contact network. The user has the option to add nodes to the social network sample.
 
 The functionality is accessed by importing the module in a python script.

 ```python
 from social_epi import sampling_social_networks as ssn
 social_network = ssn.run("contact_network_file.txt", "ssn_config.json")
 ``` 
 
 The output `social_network` is a digraph in `networkx` format. The input `contact_network_file.txt` is the `FAVITES` output file `contact_network.txt` that is available after unzipping:

 ```bash
 $ gunzip FAVITES_output/contact_network.txt.gz
 ```

 The configuration file has several parameters in `json` dictionary format:
 ```json
 {
    "interval" : 1000, 
    "burnin" : 1000, 
    "subnetwork_seed_proportion" : 0.25, 
    "degree_distribution" : {"0": 0.052, "1" : 0.186, "2" : 0.267, "3" : 0.243, "4" : 0.152, "7" : 0.005}
}
 ```
 `interval` is the sampling interval for the CCM sampler (an integer).

 `burnin` is the burnin number of samples for the CCM sampler (an integer).

 `subnetwork_seed_proportion` is the proportion of nodes that are in the fixed subnetwork of the contact network used as a seed in the social network sampler (float between 0 and 1). For example, a proportion of 0.25 means that all of the edges between nodes in a random sample of 25% of the contact network will be in the social network sample. A proportion of zero means that there is no fixed subnetwork and the CCM sample will depend only on the degree distribution of the contact network.

 `degree_distribution` is a dictionary containing the degree distribution that will be used to sample the social network via CCM. The dictionary has degrees as the keys and the probabilities of selecting those degrees as values. Only degrees with nonzero probability need to be included. All missing degrees will be filled with a very small probability. 
 

 ## Simulating Respondent-Driven Sampling

 ## Analyzing outcomes