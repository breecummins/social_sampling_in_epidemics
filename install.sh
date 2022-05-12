#!/usr/bin/bash

# installer script

# install tn93 for computing genetic distances
# cross your fingers that cmake works
mkdir -p src/tools
cd src/tools
rm -rf *
git clone git@github.com:veg/tn93.git
cd tn93
cmake .
cmake --build .
cmake --install . --prefix ~
export PATH=$PATH:$HOME/bin
cd ..
# rm -rf tn93

# install FAVITES
wget https://raw.githubusercontent.com/niemasd/FAVITES/master/run_favites_docker.py 
chmod a+x run_favites_docker.py
wget https://raw.githubusercontent.com/niemasd/FAVITES/master/run_favites_singularity.py
chmod a+x run_favites_singularity.py
cd ..

# grab the python CCM sampler and copy locally
cd social_epi
wget https://raw.githubusercontent.com/ravigoyalgit/CCMnet_py/master/inst/python/CCMnet_constr_py.py
cd ../..


# install package
pip uninstall -y social_epi &> /dev/null || True
pip install -e .