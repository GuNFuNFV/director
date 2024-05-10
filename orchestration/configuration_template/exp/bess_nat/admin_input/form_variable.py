def return_variables():
    base_list = [20]
    packet_size_list = [64]
    return [
        {
            "cuckoo_hash_entry_num": base,
            "flow_id_upper": 2 ** base,
            "packet_size": packet_size,
        } for base in base_list for packet_size in packet_size_list
    ]


def return_scaling():
    return [1]


def return_optimization_options():
    return [[]]
