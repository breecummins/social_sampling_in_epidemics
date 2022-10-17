#!/bin/bash

cp -r results results_trimmed
cd results_trimmed/JOB*

for dir in ./*/
do
   cd "$dir"
   cp FAVITES_output*/contact_network.txt .
   cp FAVITES_output*/error_free_files/transmission_network.txt .
   cp FAVITES_output*/GEMF_output/output.txt gemf_compartment_transitions.txt
   cp FAVITES_output*/GEMF_output/status.txt gemf_initial_compartments.txt
   cp FAVITES_output*/GEMF_output/README.TXT gemf_README.txt
   rm initial*
   rm overlap*
   rm *.json
   cp FAVITES_output*/GEMF_output/gemf2orig.json .
   rm -r FAVITES_output*/
   cd ..
done


