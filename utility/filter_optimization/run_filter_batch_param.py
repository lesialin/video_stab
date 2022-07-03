import os
import sys
import json
import ipdb
import glob
import shutil
from filter_optim import config_loader as cfg_loader
os.system('cp ../../code/python/config_path.py ./')
import config_path


if len(sys.argv) !=3:
    print("Please enter: python run_filter_batch_param.py dataset_dir log_prefix")
    exit()
else:

    dataset_dir = sys.argv[1]
    log_prefix = sys.argv[2]
    print("dataset_direcotry = %s"%dataset_dir)
    print("log_prefix = %s"%log_prefix)

dataset_path = dataset_dir + '/' + log_prefix + '*'
dataset_list = sorted(glob.glob(dataset_path))

#configuration path
filter_range_config_path = 'config/filter_range_config.json'
eis_config_path = config_path.eis_config_path

# load filter range configuration
alpha_min_list,alpha_max_list,beta_list,gamma_list,lookahead_no_list = \
cfg_loader.load_filter_range_config(filter_range_config_path)


filter_score_report_path = dataset_dir + '/dataset_%s_alpha_min_%.2f_%.2f_alpha_max_%.2f_%.2f_beta_%.2f_%.2f_gamma_%.2f_%.2f_lookahead_%d_%d_filter_score.csv'\
%(log_prefix,alpha_min_list[0],alpha_min_list[-1],alpha_max_list[0],alpha_max_list[-1],beta_list[0],beta_list[-1],gamma_list[0],gamma_list[-1],lookahead_no_list[0],lookahead_no_list[-1])

# write report header
filter_score_report = open(filter_score_report_path,mode='w+')
filter_score_report.write('alpha_min, alpha_max, beta,gamma,lookahead_no,')
for l in range(len(dataset_list)):
    log_dir = dataset_list[l].split('/')[-1]
    filter_score_report.write('%s,'%log_dir)
filter_score_report.write('\n')
filter_score_report.close()


# store current path
current_path = os.getcwd()

for i in range(len(beta_list)):
    for j in range(len(gamma_list)):
        for k in range(len(lookahead_no_list)):
            for p in range(len(alpha_min_list)):
                for q in range(len(alpha_max_list)):

                    beta = beta_list[i]
                    gamma = gamma_list[j]
                    lookahead_no = lookahead_no_list[k]
                    alpha_min = alpha_min_list[p]
                    alpha_max = alpha_max_list[q]
                    
                    # generate config parameters
                    config_in_js  = cfg_loader.generate_eis_config(
                        alpha_min,alpha_max,beta,gamma,lookahead_no, eis_config_path)

                    with open(eis_config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_in_js, f, sort_keys = True,ensure_ascii=False, indent=4)

                    #write parameters to report file
                    filter_score_report = open(filter_score_report_path,mode='a+')
                    filter_score_report.write('%.2f, %.2f, %.1f, %.2f, %d, '
                    %(alpha_min,alpha_max,beta,gamma,lookahead_no))
                    
                    for l in range(len(dataset_list)):
                        log_path = dataset_list[l]
                        os.chdir('../../code/python')
                        run_vid_stab_cmd = 'bash run_vid_stab.sh ' +  log_path
                        print("run_vid_stab script in:")
                        print(run_vid_stab_cmd)
                        os.system(run_vid_stab_cmd)
                        os.chdir(current_path)

                        final_score_path = log_path + '/tmp_final_score.log'
                        final_score_log = open(final_score_path,mode='r')
                        score = float(final_score_log.readline())
                        print('final score = %f'%score)
                        filter_score_report.write('%.3f,'%score)
                    filter_score_report.write('\n')
                    filter_score_report.close()

                    

os.system('rm config_path.py')
os.remove(final_score_path)