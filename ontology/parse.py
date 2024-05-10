def get_subdict(*, input: dict, field):
    # breadth first search
    temp_queue = [input]
    while len(temp_queue) > 0:
        temp_dict = temp_queue.pop(0)
        if field in temp_dict:
            return temp_dict[field]
        for key, value in temp_dict.items():
            if isinstance(value, dict):
                temp_queue.append(value)
    raise KeyError("Field {} not found in the dictionary".format(field))

def get_num(*, input: dict, field):
    return len(get_subdict(input=input, field=field))


def dict_join(dict1: dict, dict2: dict):
    # the first value in the first dict is the key, which is the id of the value in the second dict
    # we join them together to form a new dict
    temp_dict = {}
    for key, value in dict2.items():
        for key1, value1 in dict1.items():
            if key == value1:
                temp_dict[key1] = value
    return temp_dict

def filter_dict(input: dict, field, value):
    temp_dict = {}
    # search the dict for the field and value recursively
    # if found, the branch is discarded
    # if not found, the branch is kept
    for key, value_dict in input.items():
        if isinstance(value_dict, dict):
            result = filter_dict(input=value_dict, field=field, value=value)
            if result is not None:
                temp_dict[key] = result
        elif key == field and value_dict == value:
            return None
        else:
            temp_dict[key] = value_dict
    return temp_dict