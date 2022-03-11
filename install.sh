# installer script

# grab the python CCM sampler and copy locally
git clone git://github.com/ravigoyalgit/CCMnet_py
cp CCMnet_py/inst/python/CCMnet_constr_py.py src/social_epi/
rm -rf CCMnet_py

# install FAVITES
cd src/social_epi
wget https://raw.githubusercontent.com/niemasd/FAVITES/master/run_favites_docker.py 
chmod a+x run_favites_docker.py
cd ../..

# install package
pip uninstall -y social_epi &> /dev/null || True
pip install -e .