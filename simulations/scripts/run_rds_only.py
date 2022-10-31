from social_epi import nx_conversion as nxc
from social_epi import RDS_simulations as rds
from social_epi import assign_compartments as acomp
import os,glob,json,datetime


def gen_results(contacttxt,transmissiontxt,tn93dists,socialcsv,rds_config,full_dir,save_dir):
    gn,tn,sn,cn=nxc.reinflate_networks(contacttxt,transmissiontxt,tn93dists,socialcsv)
    rds_param_dict = json.load(open(rds_config))
    rds_results = rds.Assess(gn,tn,sn,cn,rds_param_dict)
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    savename = os.path.join(save_dir,"summary_{}.csv".format(timestamp))
    print(savename)
    rds_results.to_csv(savename,index=False)
    acomp.add_compartment_counts_to_summary(full_dir)


def run(rds_config,networks_folder,save_dir=None):
    networks_folder = os.path.abspath(networks_folder)
    for dir in os.listdir(networks_folder):
        full_dir = os.path.join(networks_folder,dir)
        cfile = os.path.join(full_dir,"contact_network.txt")
        tfile = os.path.join(full_dir,"transmission_network.txt")
        tn93file = os.path.join(full_dir,"tn93_distances.csv")
        sfile = glob.glob(os.path.join(full_dir,"social_network*.csv"))[0]
        if not save_dir:
            save_dir = full_dir
        else:
            save_dir = os.path.abspath(save_dir)
        gen_results(cfile,tfile,tn93file,sfile,rds_config,full_dir,save_dir)
    os.system("cp {} {}".format(rds_config,save_dir))


    
if __name__ == "__main__":
    import sys
    # first arg is an RDS configuration file, second arg is the network directory with all the TASK folders
    # e.g. results_trimmed_end/JOB758832
    # third argument is the directory in which to save the summary files, the empty string will default 
    # to the network directory
    run(sys.argv[1],sys.argv[2],sys.argv[3])    
