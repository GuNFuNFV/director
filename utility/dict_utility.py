def compare_dict(dict1: dict, dict2: dict):
    # compare them recursively
    for key in dict1:
        if key not in dict2:
            print("key: %s" % key)
            print("value: %s" % dict1[key])
            print("ground truth: %s" % dict2[key])
            return False
        if isinstance(dict1[key], dict):
            if not compare_dict(dict1[key], dict2[key]):
                return False
        else:
            if dict1[key] != dict2[key]:
                print("key: %s" % key)
                print("value: %s" % dict1[key])
                print("ground truth: %s" % dict2[key])
                return False
    return True

def convert_key_value_to_int(input_dict: dict):
    temp_dict = {}
    for key, value in input_dict.items():
        # convert key to int if possible
        try:
            key = int(key)
        except ValueError:
            pass
        # convert value to int if possible
        # catch value error or type error
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
        temp_dict[key] = value
        if isinstance(value, dict):
            temp_dict[key] = convert_key_value_to_int(value)
    return temp_dict