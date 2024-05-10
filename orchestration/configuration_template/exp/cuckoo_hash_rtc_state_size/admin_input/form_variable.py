def return_variables():
    a = [1, 2, 3, 4, 5, 6, 7, 8]
    zipped_list = list(zip(a,))
    result = []
    for i in zipped_list:
        temp_dict = {}
        temp_dict['a'] = i[0]
        result.append(temp_dict)
    return result


def return_scaling():
    return [1]
