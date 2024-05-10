# copy the file into admin_input folder and change accordingly
# the return_variables() function returns a list of dictionaries
# each dictionary is a set of variables that will be used to generate a configuration
def return_variables():
    num_possible_interleaved_threads_list = [1, 2, 4, 8, 16, 32, 64]
    cuckoo_hash_entry_num_list = [20]
    datapacking_list = [1]
    sfc_length_list = [1]
    packet_size_list = [64]
    temp_dict_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        for cuckoo_hash_entry_num in cuckoo_hash_entry_num_list:
            for datapacking in datapacking_list:
                for sfc_length in sfc_length_list:
                    for packet_size in packet_size_list:
                        temp_dict = {}
                        temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
                        temp_dict["cuckoo_hash_entry_num"] = cuckoo_hash_entry_num
                        temp_dict["datapacking"] = datapacking
                        temp_dict["sfc_length"] = sfc_length
                        temp_dict["flow_id_upper"] = 2 ** cuckoo_hash_entry_num
                        temp_dict["packet_size"] = packet_size
                        temp_dict_list.append(temp_dict)
    return temp_dict_list


def return_scaling():
    return [1]


def return_optimization_options():
    return [[]]
