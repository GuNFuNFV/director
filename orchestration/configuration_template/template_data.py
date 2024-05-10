import os

import yaml

from orchestration import NFComposer


def composed_nf_dynamic_configuration(configuration_point, instance_id):
    '''
    :param configuration_point:
    :param instance_id:
    :return: a list of (dict for configuration, instance_name) to be used to generate the configuration for each instance of the nf type in the composed nf
    '''
    # get the type of the composed nf
    composed_nf_name = configuration_point["worker_composed_nf" + "$" + instance_id]
    composed_nf_type_lst = NFComposer(composed_nf_name).get_composed_nf_and_corresponding_type()
    dict_for_configuration_and_instance_name_list = []
    for i in composed_nf_type_lst:
        instance_name = i[0]
        type_name = i[1]
        if type_name not in type_to_configuration_name:
            configuration_name = type_name
        else:
            configuration_name = type_to_configuration_name[type_name]
        configuration_dict = dynamic_configuration_name_to_dict[configuration_name]
        dict_for_configuration_and_instance_name_list.append((configuration_dict, instance_name))
    return dict_for_configuration_and_instance_name_list




static_configuration_name_to_dict = {}
current_path = os.path.dirname(os.path.abspath(__file__))
for i in os.listdir(current_path + "/static"):
    with open(current_path + "/static/" + i, "r") as f:
        static_configuration_name_to_dict[i[:-5]] = yaml.load(f, Loader=yaml.FullLoader)

#update worker_configuration in static_configuration_name_to_dict
assert "worker_configuration" in static_configuration_name_to_dict

# read the files under dynamic folder as a dict
dynamic_configuration_name_to_dict = {}
for i in os.listdir(current_path + "/dynamic"):
    if i == "type_to_configuration_name.yaml":
        continue
    with open(current_path + "/dynamic/" + i, "r") as f:
        dynamic_configuration_name_to_dict[i[:-5]] = yaml.load(f, Loader=yaml.FullLoader)
# read the type_to_configuration_name.yaml
with open(current_path + "/dynamic/type_to_configuration_name.yaml", "r") as f:
    type_to_configuration_name = yaml.load(f, Loader=yaml.FullLoader)


dynamic_configuration_name_to_func_name = {
    "composed_nf_dynamic_configuration": "composed_nf_dynamic_configuration"
}

dynamic_configuration_name_to_func = {}
for i in dynamic_configuration_name_to_func_name:
    dynamic_configuration_name_to_func[i] = globals()[dynamic_configuration_name_to_func_name[i]]

configuration_name_to_dict = {**static_configuration_name_to_dict, **dynamic_configuration_name_to_dict}


def get_options_name_with_conjecture():
    temp_list = []
    for key in configuration_name_to_dict:
        config_dict = configuration_name_to_dict[key]
        options = config_dict["options"]
        if options is None:
            continue
        for option in options:
            if "conjecture" in option:
                if option["conjecture"] == "1":
                    temp_list.append(option["name"])
    return temp_list


if __name__ == "__main__":
    print(get_options_name_with_conjecture())
