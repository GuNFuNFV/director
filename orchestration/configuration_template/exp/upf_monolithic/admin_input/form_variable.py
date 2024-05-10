def return_variables():
    interval_tree_depth_list = [4,5,6,7]
    packet_size_list = [64]
    cuckoo_hash_entry_num_list = [15,16,17,18]
    dict_list = []
    for cuckoo_hash_entry_num_list in cuckoo_hash_entry_num_list:
        for interval_tree_depth in interval_tree_depth_list:
            for packet_size in packet_size_list:
                temp_dict = {}
                temp_dict["interval_tree_depth"] = interval_tree_depth
                temp_dict["subflow_id_upper"] = (2 ** interval_tree_depth - 1) * 100
                temp_dict["packet_size"] = packet_size
                temp_dict["cuckoo_hash_entry_num"] = cuckoo_hash_entry_num_list
                temp_dict["flow_id_upper"] = 2 ** cuckoo_hash_entry_num_list
                dict_list.append(temp_dict)
    return dict_list


def return_scaling():
    return [1]


def return_optimization_options():
    return [[]]
