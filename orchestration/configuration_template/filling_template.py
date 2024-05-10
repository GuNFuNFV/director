import itertools
import os
import sys

from orchestration.configuration_template.create_exp import get_individual_key_list, Configuration_Tree, Option
from utility import red_print
from utility.file_io import get_folder_based_on_current_path, load_file
import loguru

def check_template_configuration(exp_name, template_name, admin_input_value_dic, global_options):
    template_path = get_folder_based_on_current_path("exp/" + exp_name + "/template")
    options_needed_to_fill_out = get_individual_key_list(template_name, template_path)
    filled_options = admin_input_value_dic["options"]
    filled_all_options = admin_input_value_dic["all_options"]
    # check whether global options, filled_options, filled_all_options cover all the options needed to fill out
    # print("options_needed_to_fill_out: ", options_needed_to_fill_out)
    # print("filled_options: ", filled_options)
    # print("filled_all_options: ", filled_all_options)
    for option in options_needed_to_fill_out:
        # check whether in the global options
        if option.name in global_options:
            # check whether the value is not None
            if global_options[option.name] == "None":
                pass
            else:
                continue
        # check whether in the filled_options
        if option.name in filled_options:
            # check whether the value is not None
            if filled_options[option.name] == "None":
                pass
            else:
                continue

        found = False
        # check whether in the filled_all_options
        for table_option in filled_all_options:
            if table_option['name'] == option.name:
                # check whether the path matches
                if table_option['path'] == str(option.path):
                    # check whether the value is not None
                    if table_option['value'] == "None":
                        pass  # not found
                    else:
                        found = True
        if not found:
            red_print("The option {} is not filled out".format(option.name))
            raise Exception("The option %s is not filled out".format(option.name))
    return True


def fill_template_dic(template_dic, option_list, path="root"):
    for key in template_dic.keys():
        if isinstance(template_dic[key], dict):
            fill_template_dic(template_dic[key], option_list, path + "/" + key)
        else:
            for option in option_list:
                if path + "/" + key == option.path:
                    template_dic[key] = option.value
                    break
    return template_dic


def output_final_configuration_file(exp_name, option_list, id):
    result_dic = {}
    for option in option_list:
        option_name = option.name
        option_path = str(option.path).split("/")
        current_dic = result_dic

        for i in range(1, len(option_path) - 1):
            if option_path[i] not in current_dic:
                current_dic[option_path[i]] = {}
            current_dic = current_dic[option_path[i]]
        if option_path[-1] == "":
            current_dic[option_name] = option.value
        else:
            current_dic[option_path[-1]][option_name] = option.value
    output_path = get_folder_based_on_current_path("exp/" + exp_name + "/output")
    # create the output folder if not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    file_name = str(id) + ".yaml"
    with open(os.path.join(output_path, file_name), "w") as f:
        # dump as yaml
        import yaml
        yaml.dump(result_dic, f, default_flow_style=False, sort_keys=False)
    return result_dic


def evaluate(value, config_dic):
    if type(value) == int:
        return value
    if value[0] == "%" and value[-1] == "%":
        return config_dic[value[1:-1]]
    else:
        return value


def fill_out_template(exp_name, template_name, admin_input_value_dic, global_options, config):
    filled_options = admin_input_value_dic["options"]
    filled_all_options = admin_input_value_dic["all_options"]

    # load template as a dictionary
    template_path = get_folder_based_on_current_path("exp/" + exp_name + "/template")
    template_dic = load_file(os.path.join(template_path, template_name))
    # print("template_dic: ", template_dic)
    configuration_tree = Configuration_Tree(template_dic)
    options = configuration_tree.node_collect_options()
    temp_result = []
    for option in options:
        if type(option.value) == int:
            continue
        if option.value[0] == "%" and option.value[-1] == "%":
            temp_result.append(option)
    for option in temp_result:
        option_name = option.name
        option_path = str(option.path)
        filled_by_global = False
        filled_by_filled_options = False
        filled_by_filled_all_options = False
        if global_options[option_name] != "None":
            option.value = evaluate(global_options[option_name], config)
            filled_by_global = True

        if option_name in filled_options:
            if filled_options[option_name] != "None":
                option.value = evaluate(filled_options[option_name], config)
                filled_by_filled_options = True

        for item in filled_all_options:
            if item["name"] == option_name and item["path"] == option_path:
                if item["value"] != "None":
                    option.value = evaluate(item["value"], config)
                    filled_by_filled_all_options = True

        filled_by = "filled_by_all_options" if filled_by_filled_options else "filled_by_filled_options" if filled_by_filled_all_options else "filled_by_global" if filled_by_global else "not_filled_out"
        # print("option name {}:{} is filled out by {}".format(option_name, option.value, filled_by))
    return options


def fill_out_templates(exp_name, admin_input_dict, config) -> list[list[Option]]:
    global_options = admin_input_dict["global_options"]
    template_options = admin_input_dict["template_options"]
    template_name = ""
    options_list = []
    try:
        for template_name in template_options:
            template_dic = template_options[template_name]
            new_options = fill_out_template(exp_name, template_name, template_dic, global_options, config)
            options_list.append(new_options)
        return options_list
    except Exception as e:
        red_print("template {} is not valid".format(template_name))
        raise e


def check_configuration(exp_name, admin_input_dict, variable_dict):
    global_options = admin_input_dict["global_options"]
    template_options = admin_input_dict["template_options"]
    template_name = ""
    try:
        for template_name in template_options:
            template_dic = template_options[template_name]
            if not check_template_configuration(exp_name, template_name, template_dic, global_options):
                return False
    except Exception as e:
        red_print("template {} is not valid".format(template_name))
        raise e
    # print("The configuration is valid")
    return True


def get_exp_options(exp_name):
    # all the files in the admin_input folder in the exp folder
    folder_path = get_folder_based_on_current_path("exp/" + exp_name + "/admin_input")
    # list all the files in the folder and get their full path
    file_list = os.listdir(folder_path)
    file_list = [os.path.join(folder_path, file) for file in file_list]
    # filter out the files that are not yaml files
    file_list = [file for file in file_list if file.split(".")[-1] == "yaml"]
    configuration_dict_list = []
    options = []
    scaling = [1]
    optimization_options = []
    try:
        file_name = folder_path + "/form.yaml"
        admin_input_dict = load_file(file_name)
        variable_file_name = file_name.split(".")[0] + "_variable.py"
        # assert the variable file exists
        assert os.path.exists(variable_file_name)
        # get all the variables in the variable file
        variable_dict = {}
        if os.path.exists(variable_file_name):
            # import the variable file and its return_variables function
            import importlib.util
            spec = importlib.util.spec_from_file_location("module.name", variable_file_name)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            variable_dict = foo.return_variables()
            scaling = foo.return_scaling()
            # if it contains return_scaling function, then use it
            if hasattr(foo, "return_scaling"):
                scaling = foo.return_scaling()
            else:
                scaling = [1]
            # if it contains return_optimization_options function, then use it
            if hasattr(foo, "return_optimization_options"):
                optimization_options = foo.return_optimization_options()
            else:
                optimization_options = None
            # print("variable_dict: ", variable_dict)
        if variable_dict == {}:
            # check if the configurations are valid
            result = check_configuration(exp_name, admin_input_dict, None)
            if result:
                new_options = fill_out_templates(exp_name, admin_input_dict, None)
                options.extend(new_options)
        else:
            for config in variable_dict:
                # check if the configurations are valid
                result = check_configuration(exp_name, admin_input_dict, config)
                if result:
                    new_options = fill_out_templates(exp_name, admin_input_dict, config)
                    options.extend(new_options)
        return options, scaling, optimization_options
    except Exception as e:
        red_print("The configuration for {} is not valid".format(file_name))
        raise e


def unpack_option(option_list: list[Option]) -> list[list[Option]]:
    key_list = []
    path_list = []
    value_list = []
    for temp_option in option_list:
        key_list.append(temp_option.name)
        path_list.append(temp_option.path)
        if type(temp_option.value) == list:
            value_list.append(temp_option.value)
        else:
            value_list.append([temp_option.value])

    # key_list and path_list into a list of tuple
    key_path_list = list(zip(key_list, path_list))

    # take cartesian product on the value list
    vector_values = list(itertools.product(*value_list))

    result = []
    for vector_value in vector_values:
        unpacket_option_list = []
        for i in range(len(key_path_list)):
            name = key_path_list[i][0]
            path = key_path_list[i][1]
            value = vector_value[i]
            unpacked_option = Option(name, value, path)
            unpacked_option.name = name
            unpacked_option.path = path
            unpacked_option.value = value
            unpacket_option_list.append(unpacked_option)
        result.append(unpacket_option_list)

    return result


def get_configuration_dict_list(exp_name) -> list[dict]:
    packet_options_list,scaling_worker,optimization_options = get_exp_options(exp_name)
    result = packet_options_list

    result_dic_list = []
    for i, option_list in enumerate(result):
        result = output_final_configuration_file(exp_name, option_list, i)
        result_dic_list.append(result)
    return result_dic_list, scaling_worker, optimization_options


if __name__ == '__main__':
    '''
    fill out the form
    usage: python3 filling_template.py exp_name=... 
    '''
    exp_name = ""
    for arg in sys.argv[1:]:
        if arg.startswith("exp_name="):
            exp_name = arg.split("=")[1]

    if exp_name == "":
        exp_name = "interleaved_experiments"

    print(get_configuration_dict_list(exp_name))
