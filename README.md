# Overview

`social_epi` is a package for generating contact, transmission, and phylogenetic cluster networks of epidemic spread of a sexually transmitted disease (e.g., HIV), generating social networks based on the contact networks and additional parameters, and performing peer recruitment strategies, e.g. respondent driven sampling (RDS), on the social and (sexual) contact networks. The purpose to compare the performance of these sampling strategies on the social and contact networks in identifying disease-positive individuals, as well as direct and indirect transmission links.

See the manuscript "Leveraging social networks for identification of people living with HIV and high transmission potential", Cummins et al. (2023) and the README in `simulations/study_parameters_20220929` for more details.

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

To make sure that the `tn93` tool is available at all times, you will need to add the line 
```bash
export PATH=$PATH:$HOME/bin
```
to your `.bashrc` or `.bash_profile`.

 # Usage

 ## Main program

 To run the program start to finish (network sampling, epidemic, and peer recruitment strategies), write configuration files and do 

 ```bash
 $ python run_simulations.py <contact_config.json> <favites_config.txt> <social_config.json> <rds_config.json> <results_dir> <favites_version> <path/to/docker-singularity-script>
 ```

Each of the components in `run_simulations.py` is discussed separately below, together with configuration file information.
The input `favites_version` is optional and defaults to `latest`.
    The input `path/to/docker-singularity-script` is also optional and defaults to `src/tools/run_favites_docker.py`. However, it is likely that to run `run_simulations.py`, a modified docker file will need to be written that mounts local files. See `simulations/scripts/` for modified versions of `run_favites_docker.py`. 

The output is a `csv` file containing the column names `SN GN count`, `SN GN total`, `CN GN count`, `CN GN total`, `SN TN count`, `SN TN total`, `CN TN count`, `CN TN total`, `SN sampled`, `CN sampled`, `SN seed`, `CN seed`, , `SN HIV+`, `CN HIV+`, the names of all the compartments, and two columns listing isolated nodes. `SN` stands for social network, `CN` stands for contact network, `GN` stands for genetic cluster network, and `TN` stands for transmission network. `SN GN count` has as values the count of sampled pairs of individuals in the social network that appear as a pair (edge) in the genetic cluster network. Similarly for the other columns ending in `count`. The column names ending in `total` refer to the total number of such pairs available to be discovered via sampling. `SN sampled` and `CN sampled` have the sample sizes recovered by the peer recruitment strategies. The `seed` columns give the nodes (individuals) that were the initial sample for the peer recruitment strategies. The `HIV+` columns report the total number of infected individuals sampled. The columns with compartment names list the number of individuals in that compartment at epidemic simulation end that were recovered via sampling. The `isolated` columns list how many isolated nodes were in the original social and contact networks, and therefore were dropped from the epidemic simulation.

**Note that the compartment assignments in the results from `run_simulations.py` are tailored to the specific model in `simulations/study_parameters_20220929`. This is due to solely to the analysis in the `assign_compartments.py` module.** To implement a different compartmental model, see details in the FAVITES section below and do not rely on the compartment assignments in the output file (or write a different version of `assign_compartments.py`). 



 ## Generating contact network, transmission network, and genetic sequences from an epidemic compartmental model

 To run FAVITES, create a configuration file (an example is `tests/favites_hiv_test_config.txt` or see multiple versions in `simulations/study_parameters_20220929`). General documentation for FAVITES is here: https://github.com/niemasd/FAVITES/wiki, and is particularly good at explaining the parameters for the genetic sequence evolutionary model. The following lists parameters that were especially important during our simulations of an HIV epidemic.

  * `TimeSample`: The time at which to sequence an infected individual, such as `End` (end of the simulation), `Infection` (at the time of infection), and `GranichFirstART` (at the time of diagnosis). See the FAVITES documentation for other options.

 * `num_seeds`: The number of infected individuals at simulation start.

 * `hiv_freq_X`: The initial number of individuals in compartment `X`. The sum of `hiv_freq_X` over all compartments `X` (excluding `s`, `ns`, and `d`) must sum to `num_seeds`. `hiv_freq_s` + `num_seeds` is the total population.

 * `end_time`: The length of the simulation in some time unit. The transition rates below must also be in the same units, but the units never need to be specified.

 * `hiv_X_to_Y`: The transition rate from compartment `X` to compartment `Y`. The reciprocal of the rate (the expected time interval to transition) is taken to be the mean of a Poisson distribution that controls the number of transitions from `X` to `Y` per time point.

 * `hiv_s_to_i1_by_X`: The infection rate given a sexual contact between a susceptible individual and an infected individual from compartment `X`.

 Compartment `s` is always the susceptible group, `ns` is not susceptible (i.e., not infected and will not become infected), `i1` is always the initially infected group, and `d` is always the death compartment. The other compartments (`a1`-`a4` and `i2`-`i4`) all represent infected individuals that are at various stages of the disease or are under treatment. Interpretations can vary slightly as needed for a particular compartmental model. Nonzero transmission rates determine the network architecture of the compartmental model. For example, if `hiv_a1_to_a2` is assigned a positive value, it means that there is an arrow from compartment `a1` to `a2`. If it is assigned 0, there is no edge between compartments. **It is important to realize that not all transitions are permitted.** See the FAVITES documentation for allowed wiring diagrams. Some disallowed architectures can be approximated using dummy compartments and infinite transition rates (see e.g. `simulations/study_parameters_20220929/README.md` for an example).

 The sexual contact network on which to run the epidemic model is generated by `CCMnet_py` within the FAVITES package. FAVITES can either be passed a contact network configuration file (with a modified `run_docker` script), or can directly take the list of parameters. In both cases, the FAVITES parameter `ContactNetworkGenerator` is set to `CCMnetPy`.

 To pass a contact network configuration file, then set the following parameter in the FAVITES configuration file.

 * `cn_config_file`: The full path to a configuration file for contact network sampling. This requires a modified `run_favites_docker.py` file (see examples in `simulations/scripts`). 

 Most of the parameters inside the contact network configuration are set to sensible defaults in `CCMnet_constr_py.py`. The parameters that are likely to be changed are the following.

 * `degree_distribution`: A dictionary of degree: probability pairs, where the degree is stringified, e.g. `{"0" : 0.089, "1" : 0.354, "2" : 0.189, "3" : 0.146, "4" : 0.089, "5" : 0.128, "6" : 0.005}` and the values sum to 1.
* `small_prob`: A very small probability, e.g. 10<sup>-6</sup>, that will pad all degrees not included in the dictionary.
* `population`: The number of nodes in the sexual contact networks.
* `burnin`: The number of burn-in iterations before sampling starts.
* `G` : (Optional) A full path to a csv with an initial graph to start with in the Metropolis-Hastings algorithm. This requires a modified `run_favites_docker.py` file (see examples in `simulations/scripts`). 
* `use_G`: Set to 1 if `G` is used, 0 otherwise. 

 To run the epidemic model, do
 ```bash
$ cd <desired_results_folder>
$ python <path/to/social_sampling_in_epidemics>/src/tools/run_favites_docker.py -u latest -c <path/to/config>
 ```

 The results will be in a `FAVITES_output` directory. Old results in an existing folder with the same name will be overwritten. The files include a contact network file (`contact_network.txt.gz`), a transmission network file (`transmission_network.txt.gz`), a file containing the record of epidemic transmissions (`gemf_compartment_transitions.txt`), and multiple fastq/fasta sequence files. The sequence file to be used in future steps is `sequence_data.fasta.gz`. Unzip before proceeding to the next steps:

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

 The function `sampling_social_networks.py` accepts a contact network and produces a single random social network based on features of the contact network. In particular, a random subgraph of the contact network is held fixed and a `CCMnet_py` network sample is drawn according to the degree distribution of the contact network. 
 
 The functionality is accessed by importing the module in a python script.

 ```python
 from social_epi import sampling_social_networks as ssn
 
 social_network = ssn.run("contact_network_file.txt", "ssn_config.json")
 ``` 
 
 The output `social_network` is a digraph in `networkx` format. The input `contact_network_file.txt` is the `FAVITES` output file `contact_network.txt` that is available after unzipping:

 ```bash
 $ gunzip FAVITES_output/contact_network.txt.gz
 ```

 To save the social network as a `csv` file, do

 ```python
from social_epi import nx_conversion as nxc

SNdf = nxc.nx2pandas(social_network)
SNdf.to_csv("social_network.csv",index=False)
 ```

 The configuration json file only needs a subset of the parameters for the sexual contact network, plus one additional parameter for the proportion of overlap between the sexual and social networks, plus a couple of file names under which to save the initial social graph that is generated to launch CCM and a modified version of the configuration file with more parameters automatically generated. An example configuration file is given below.
 ```json
 {
    "degree_distribution" : {"0": 0.052, "1" : 0.186, "2" : 0.267, "3" : 0.243, "4" : 0.152, "7" : 0.005},
    "small_prob" : 0.000000001, "burnin" : 1000, 
    "network_overlap" : 0.13, 
    "savename_initial" : "initial_social_network.csv",
    "savename_ccm_config" : "social_ccm_config.json"
}
 ```
 
 ## Simulating peer recruitment strategies

To simulate peer recruitment strategies on the generated social and contact networks, write a configuration file and do

```python
from social_epi import RDS_simulations as rds

output = rds.run_from_files(contacttxt,transmissiontxt,tn93dists,socialcsv,rds_config)
```

The inputs are all paths to files. `contacttxt` and `transmissiontxt` are the unzipped contact and transmission network files from FAVITES. `tn93dists` is the output file from running `tn93`, and `social_csv` is the output file from generating the social network. The last argument is the peer recruitment `json` configuration file. Here is an example.

```json
{
    "SNwaves" : 600,
    "CNwaves" : 0,
    "SNcoupons" : 6,
    "CNcoupons" : 15937,
    "SNprob" : 0.394,
    "CNprob" : 0.175,
    "SNsize" : 600,
    "CNsize" : 15397,
    "SNseeds" : 62,
    "CNseeds" : 62,
    "SNposseed" : true,
    "CNposseed" : true,
    "SNposwave" : false,
    "CNposwave" : true
}
```

Again, `SN` stands for social network and `CN` stands for contact network. The `size` parameters limit the sample size to be collected. Use the number of nodes in the network if there is no limit. The `waves` parameters indicate the maximum number of recruitment waves that are permitted. Set to the sample size to ensure that the desired sample size is reached, and set to zero if the waves are unlimited. The `coupons` parameter indicates the maximum number of recruits permitted per individual. The `prob` parameters indicate coupon acceptance probability. The `seeds` parameters indicate the number of individuals that start the recruiting process. The `posseed` parameters indicate whether the seed individuals are all infected (`true`) or can be mixed infected/uninfected (`false`). The `poswave` parameters indicate if only infected  individuals are given coupons to continue recruiting (`true`), or if any recruited individual can continue recruiting (`false`).

The output is a pandas dataframe with the following columns:
`SN GN count`, `SN GN total`, `CN GN count`, `CN GN total`,`SN TN count`,`SN TN total`,`CN TN count`,`CN TN total`,`SN sampled"`,`CN sampled"`,`SN seed`, `CN seed`, `SN HIV+`, and `CN HIV+`. The meaning of these columns is described in the Main Program section.
 
 