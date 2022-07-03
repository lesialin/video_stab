import json
import ipdb

def generate_eis_config(alpha_min,alpha_max,beta,gamma,lookahead_no, eis_config_path):

    with open(eis_config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())
    
    config_in_js["alpha_min"] = alpha_min
    config_in_js["alpha_max"] = alpha_max
    config_in_js["beta"] = beta
    config_in_js["gamma"] = gamma
    config_in_js["lookahead_no"] = lookahead_no

    return config_in_js
    


def load_filter_range_config(config_path):
    
    with open(config_path , 'r') as reader:
        config_in_js = json.loads(reader.read())

    alpha_min_range =  config_in_js["alpha_min_range"]
    alpha_max_range =  config_in_js["alpha_max_range"]
    beta_range = config_in_js["beta_range"]
    gamma_range = config_in_js["gamma_range"]
    lookahead_no_range = config_in_js["lookahead_no_range"]


    # create alpha min list
    param_range = alpha_min_range
    param_min = param_range[0]
    param_max = param_range[1]
    param_interv = param_range[2]
    param = param_min
    param_list = []
    while param <= param_max:
        param_list.append(param)
        param += param_interv
        param = round(param,2)

    alpha_min_list = param_list


    # create alpha max list
    param_range = alpha_max_range
    param_min = param_range[0]
    param_max = param_range[1]
    param_interv = param_range[2]
    param = param_min
    param_list = []
    while param <= param_max:
        param_list.append(param)
        param += param_interv
        param = round(param,2)

    alpha_max_list = param_list
        

    # create beta list
    param_range = beta_range
    param_min = param_range[0]
    param_max = param_range[1]
    param_interv = param_range[2]
    param = param_min
    param_list = []
    while param <= param_max:
        param_list.append(param)
        param += param_interv
        param = round(param,1)

    beta_list = param_list

    # create gamma list
    param_range = gamma_range
    param_min = param_range[0]
    param_max = param_range[1]
    param_interv = param_range[2]
    param = param_min
    param_list = []
    while param <= param_max:
        param_list.append(param)
        param += param_interv
        param = round(param,2)
        

    gamma_list = param_list

    # create lookahead list
    param_range = lookahead_no_range
    param_min = param_range[0]
    param_max = param_range[1]
    param_interv = param_range[2]
    param = param_min
    param_list = []
    while param <= param_max:
        param_list.append(param)
        param += param_interv

    lookahead_no_list = param_list

    return alpha_min_list,alpha_max_list,beta_list,gamma_list,lookahead_no_list
