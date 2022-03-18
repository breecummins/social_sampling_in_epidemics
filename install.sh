#!/usr/bin/bash

# installer script

# install tn93 for computing genetic distances
# cross your fingers that cmake works
mkdir tools
cd tools
git clone git@github.com:veg/tn93.git
cd tn93
sudo cmake .
sudo make install
cd ..
# rm -rf tn93

# install FAVITES
wget https://raw.githubusercontent.com/niemasd/FAVITES/master/run_favites_docker.py 
chmod a+x run_favites_docker.py
wget https://raw.githubusercontent.com/niemasd/FAVITES/master/helper_scripts/tn93_to_clusters.py 
chmod a+x tn93_to_clusters.py
cd ..

# grab the python CCM sampler and copy locally
cd src/social_epi
wget https://raw.githubusercontent.com/ravigoyalgit/CCMnet_py/master/inst/python/CCMnet_constr_py.py src/social_epi/
cd ../..


# install package
pip uninstall -y social_epi &> /dev/null || True
pip install -e .