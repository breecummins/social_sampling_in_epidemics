#!/bin/bash

cp -r results results_trimmed
cd results_trimmed/JOB*

for dir in ./*/
do
   cd "$dir"
   cp FAVITES_output*/contact_network.txt .
   cp FAVITES_output*/error_free_files/transmission_network.txt .
   cp FAVITES_output*/GEMF_output/README.TXT gemf_README.txt
   rm initial*
   rm overlap*
   rm -r FAVITES_output*/
   cd ..
done


