# copy the file into admin_input folder and change accordingly
# the return_variables() function returns a list of dictionaries
# each dictionary is a set of variables that will be used to generate a configuration
def return_variables():
    cuckoo_hash_entry_num_list = [17]
    # current_cstate_list = [1, 2, 3, 5, 6]
    current_cstate_list = [1]
    temp_dict_list = []
    for cuckoo_hash_entry_num in cuckoo_hash_entry_num_list:
        for current_cstate in current_cstate_list:
            temp_dict = {
                "cuckoo_hash_entry_num": cuckoo_hash_entry_num,
                "current_cstate": current_cstate,
                "flow_id_upper": 2 ** cuckoo_hash_entry_num
            }
            temp_dict_list.append(temp_dict)
    return temp_dict_list


def return_scaling():
    return [1, 2, 3, 4, 5, 6, 7, 8]


def return_optimization_options():
    return [[]]
