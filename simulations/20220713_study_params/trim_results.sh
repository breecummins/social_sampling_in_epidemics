#!/bin/bash

# cp -r results results_trimmed
cd results_trimmed/JOB*
echo $PWD

for dir in ./*/
do
   cd "$dir"
   cd ..
done

# for dir in `ls`
# do
#    cd $dir
#    cp FAVITES_output*/contact_network.txt .
#    cp FAVITES_output*/error_free_files/transmission_network.txt .
#    rm initial*
#    rm overlap*
#    rm *.json
#    rm -r FAVITES_output*/
# done


