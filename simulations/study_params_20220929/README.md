# Figures for "Leveraging social networks for identification of people living with HIV and high transmission potential", Cummins et al. (2023)

## Figure Generation

**To generate the figures in the paper, run the Jupyter notebook ```visualize_results.ipynb```.**

## Configuration files containing simulation parameters
All figures used `contact_config.json` and `sampling_social_networks_config.json` for sampling sexual and social contact networks, respectively. 

* Figure 3: `favites_hiv_config_end.txt` and `rds_config.json`.

* Figure 4: `favites_hiv_config_end.txt`

* Figure 5: `favites_hiv_config_end.txt` and `rds_config_contact.json`.

* Figure 6: `favites_hiv_config_end.txt` and `rds_config.json` with `SN_prob` and `CN_prob` repeatedly altered as explained in text for the social and sexual contact acceptance rates, respectively. See also the `rds_config.json` files in the subfolders of `sensitivity_analysis_acceptance`.

* Figure 7: `rds_config.json`, with, from left to right, `favites_hiv_config_end.txt`, `favites_hiv_config_75prevalence.txt`, `favites_hiv_config_50prevalence.txt`, and `favites_hiv_config_25prevalence.txt`.  

* Supplementary Figure S1: `favites_hiv_config_infection.txt`.

## Compartmental Model

The compartments in the compartmental model in the paper are described as susceptible, acute undiagnosed, chronic undiagnosed, acute treated, chronic treated, and out-of-care. The correspondence between these compartments and FAVITES parameter notation is as follows.

| Model compartment   | FAVITES compartment |
|---------------------|---------------------|
| Susceptible         | `s`                 |
| Acute undiagnosed   | `i1`                |
| Chronic undiagnosed | `i2`                |
| Out-of-care         | `i3`                |
| Acute treated       | `a1`                |
| Dummy compartment   | `a2`                |
| Chronic treated     | `a3`                |

The dummy compartment `a2` is included due to limitations in the connections between compartments permitted by FAVITES. Compartments `i2` and `a1` both transition into `a2`, which then has an infinite transition rate into compartment `i3`.

