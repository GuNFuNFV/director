# def return_variables():
#     interval_tree_depth_list = [4,5,6,7]
#     num_possible_interleaved_threads_list = [1,2,4,8,16,32,64,128]
#     dict_list = []
#     for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
#         for interval_tree_depth in interval_tree_depth_list:
#             temp_dict = {}
#             temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
#             temp_dict["interval_tree_depth"] = interval_tree_depth
#             temp_dict["subflow_id_upper"] = (2 ** interval_tree_depth - 1) * 100
#             dict_list.append(temp_dict)
#     return dict_list

def return_variables():
    interval_tree_depth_list = [4, 5, 6, 7]
    num_possible_interleaved_threads_list = [16]
    packet_size_list = [1512]
    dict_list = []
    for num_possible_interleaved_threads in num_possible_interleaved_threads_list:
        for interval_tree_depth in interval_tree_depth_list:
            for packet_size in packet_size_list:
                temp_dict = {}
                temp_dict["num_possible_interleaved_threads"] = num_possible_interleaved_threads
                temp_dict["interval_tree_depth"] = interval_tree_depth
                temp_dict["subflow_id_upper"] = (2 ** interval_tree_depth - 1) * 100
                temp_dict["packet_size"] = packet_size
                dict_list.append(temp_dict)
    return dict_list


def return_scaling():
    return [3,4,5,6]


def return_optimization_options():
    return [[]]
