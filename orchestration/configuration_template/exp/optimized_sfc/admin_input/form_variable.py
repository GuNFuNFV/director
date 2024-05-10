def return_variables():
    # num_possible_interleaved_threads_list = [1,2,4,8,16,32]
    num_possible_interleaved_threads_list = [16]
    packet_size_list = [64, 128, 256, 512, 1024, 1280, 1518]
    varaible_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        for packet_size in packet_size_list:
            temp_dict = {}
            temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
            temp_dict["packet_size"] = packet_size
            varaible_list.append(temp_dict)
    return varaible_list

def return_scaling():
    return [1]

def return_optimization_options():
    return [
        # [],
        # ["data_packing"],
        ["data_packing", "redundant_match_removal"]
    ]
