def return_variables():
    prefetch_mode = [0,1,2,3]
    packet_size = [128]
    result = []
    for i in prefetch_mode:
        for j in packet_size:
            temp_dict = {}
            temp_dict['prefetch_mode'] = i
            temp_dict['packet_size'] = j
            result.append(temp_dict)
    return result
def return_scaling():
    return [1]
def return_optimization_options():
    return [[]]
