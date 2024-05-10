def return_variables():
    # a = [14,15,16,17,18,19,20]
    # a =  [17, 18, 19, 20]
    a = [20]
    packet_size = [64, 128, 256, 512, 1024, 1280, 1512]
    b = []
    for i in a:
        b.append(2 ** i)
    zipped_list = list(zip(a, b))
    result = []
    for i in zipped_list:
        for j in packet_size:
            temp_dict = {}
            temp_dict['a'] = i[0]
            temp_dict['b'] = i[1]
            temp_dict['packet_size'] = j
            result.append(temp_dict)
    return result


def return_scaling():
    return [1]


if __name__ == "__main__":
    print(return_variables())
