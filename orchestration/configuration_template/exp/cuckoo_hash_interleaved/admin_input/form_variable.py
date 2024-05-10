def to_array_of_dict(key_list, zipped_list):
    result = []
    for i in zipped_list:
        temp_dict = {}
        for j in range(len(key_list)):
            temp_dict[key_list[j]] = i[j]
        result.append(temp_dict)
    return result


def return_variables():
    num_possible_interleaved_threads_list = [1,2,4,8,16]
    cuckoo_hash_entry_num_list = [16]
    packet_size_list = [64]

    varaible_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        for cuckoo_hash_entry_num in cuckoo_hash_entry_num_list:
            for packet_size in packet_size_list:
                temp_dict = {}
                temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
                temp_dict["flow_id_upper"] = 2 ** cuckoo_hash_entry_num
                temp_dict["packet_size"] = packet_size
                temp_dict["cuckoo_hash_entry_num"] = cuckoo_hash_entry_num
                varaible_list.append(temp_dict)
    return varaible_list


def return_scaling():
    return [1]


def exp_2_return_variables():
    num_possible_interleaved_threads_list = [16]
    flow_id_upper_list = [2 ** 20]
    packet_size_list = [64, 128, 256, 512, 1024]
    varaible_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        for packet_size in packet_size_list:
            temp_dict = {}
            temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
            temp_dict["flow_id_upper"] = flow_id_upper_list[0]
            temp_dict["packet_size"] = packet_size
            varaible_list.append(temp_dict)
    return varaible_list
