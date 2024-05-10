# copy the file into admin_input folder and change accordingly
# the return_variables() function returns a list of dictionaries
# each dictionary is a set of variables that will be used to generate a configuration
def return_variables():
    probabililty = [50, 100]
    temp_dict_list = []
    for i in probabililty:
        temp_dict_list.append({
            'probability': i
        })
    return temp_dict_list


def return_scaling():
    return [1]


def return_optimization_options():
    return [[]]
