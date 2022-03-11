from setuptools import setup, find_packages

setup(name='social_epi',
      version='0.1',
      description='Social network sampling and RDS simulation for approximating transmission networks',
      url='https://github.com/breecummins/social_sampling_in_epidemics',
      author='Bree Cummins, Ravi Goyal, and Kara Johnson',
      author_email='breschine.cummins@montana.edu, r1goyal@health.ucsd.edu, kara.johnson4@montana.edu',
      license='MIT',
      packages=find_packages("src", exclude=["social_epi_app-0.1.0"]),
      package_dir={'':'src'},
      zip_safe=False)