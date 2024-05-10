def return_variables():
    num_possible_interleaved_threads_list = [1, 2, 4, 8, 16, 32]
    num_possible_interleaved_threads_list = [16]
    cuckoo_hash_entry_num_list = [20]
    # packet_size_list = [64, 128, 256, 512]
    packet_size_list = [64, 128,256, 512]
    dict_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        temp_dict = {}
        temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
        for cuckoo_hash_entry_num in cuckoo_hash_entry_num_list:
            temp_dict["cuckoo_hash_entry_num"] = cuckoo_hash_entry_num
            temp_dict["flow_id_upper"] = 2 ** cuckoo_hash_entry_num
            for packet_size in packet_size_list:
                temp_dict["packet_size"] = packet_size
                dict_list.append(temp_dict.copy())
    return dict_list


def return_scaling():
    return [1]


def return_optimization_options():
    return [[]]
