'''
This module is used to generate form that the admin needs to fill out for all the parameters that needed to be set
'''
import getopt
import os
import shutil
import sys
from collections import OrderedDict

import yaml

from utility import Tree
from utility.file_io import return_file_name_from_folder
from utility.tree_from_dic import TreeNode, tree_path
from dataclasses import dataclass


class Option:
    def __init__(self, option: str, value: str | int, path: tree_path):
        self.name = option
        self.value = value
        self.path = path

    def get_instance_information(self):
        temp = str(self.path).split("/")
        temp_result = []
        for i in range(1, len(temp)):
            # split #
            temp_result.append(temp[i].split("#"))
        return temp_result


class Configuration_Tree(Tree):
    def __init__(self, data):
        super().__init__(data)

    def node_collect_options(self, node: TreeNode = None) -> list[Option]:
        if node is None:
            node = self.root
        result = []
        for key in node.value_dict:
            path = tree_path()
            path.add_node(node)
            result.append(Option(key, node.value_dict[key], path))
        if len(node.children) > 0:
            for child in node.children:
                temp = self.node_collect_options(child)
                for j in range(len(temp)):
                    temp_result = temp[j]
                    temp_result.path.add_node(node)
                    result.append(temp_result)
        return result

available_values = {
    "machine_ip": ["128.101.118.41", "128.101.118.40"],
    "num_possible_interleaved_threads": ["1", "2", "4", "8", "16", "32", "64"],
    "cuckoo_hash_entry_num": ["14", "15", "16", "17", "18", "19", "20"],
    "cuckoo_hash_header_type": ["0", "1"],
    "cuckoo_hash_key_size": ["16"],
    "generic_access_mode": ["0", "1"],
    "generic_access_size": ["1", "2", "4", "8"],
    "flow_id_lower": None,
    "flow_id_upper": None,
    "packet_size": ["64", "128", "256", "512"],
    "proportion": None,
    "subflow_id_lower": None,
    "subflow_id_upper": None
}


def get_unique_key_list(template_file_name):
    import os
    current_path = os.path.dirname(os.path.abspath(__file__))
    template_file_name = os.path.join(current_path + "/template", template_file_name)
    # read template_file as a dictionary named result
    with open(template_file_name, "r") as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
    a = Configuration_Tree(result)
    options = a.node_collect_options()
    # input the options that you want to have fixed across sub-structure
    unique_options = []
    for option in options:
        if option.name in unique_options:
            continue
        else:
            # if option_value start wth % and end with %, it is a variable that may need to be changed
            try:
                if option.value[0] == "%" and option.value[-1] == "%":
                    unique_options.append(option.name)
            except:
                continue # if option_value is not a string, it is a number, and it is not a variable
    return unique_options


def get_individual_key_list(template_file_name, template_file_folder_path = None)->list[Option]:
    import os
    if template_file_folder_path is None:
        current_path = os.path.dirname(os.path.abspath(__file__))
        template_file_full_path = os.path.join(current_path + "/template", template_file_name)
    else:
        template_file_full_path = os.path.join(template_file_folder_path, template_file_name)
    # read template_file as a dictionary named result
    with open(template_file_full_path, "r") as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
    a = Configuration_Tree(result)
    options = a.node_collect_options()
    temp_result = []
    for option in options:
        if type(option.value) == int:
            continue
        if option.value[0] == "%" and option.value[-1] == "%":
            temp_result.append(option)
    return temp_result


def create_exp(exp_dict):
    exp_name = exp_dict["exp_name"]
    template_file_list = exp_dict["template_file_list"]
    # create a folder named exp_name in exp folder
    current_path = os.path.dirname(os.path.abspath(__file__))
    exp_path = os.path.join(current_path, "exp", exp_name)
    if not os.path.exists(exp_path):
        os.mkdir(exp_path)

    form = {}

    # output the form to a yaml file in the exp path
    form_file_path = os.path.join(exp_path, "form.yaml")
    with open(form_file_path, "w") as f:
        yaml.dump(form, f)

        # create a folder named exp_name in exp folder
        current_path = os.path.dirname(os.path.abspath(__file__))
        exp_path = os.path.join(current_path, "exp", exp_name)
        if not os.path.exists(exp_path):
            os.mkdir(exp_path)

        form = dict()
        template_to_unique_key_list = {}
        form["global_options"] = {}
        form["template_options"] = {}
        for template_file_name in template_file_list:
            template_file_path = os.path.join(current_path, "template", template_file_name)
            template_to_unique_key_list[template_file_name] = get_unique_key_list(template_file_path)
        for template_file_name in template_to_unique_key_list:
            form["template_options"][template_file_name] = {}
            unique_key_list = template_to_unique_key_list[template_file_name]
            form["template_options"][template_file_name]["options"] = {}
            for unique_key in unique_key_list:
                form["template_options"][template_file_name]["options"][unique_key] = "None"
                form["global_options"][unique_key] = "None"

        template_to_all_options = {}
        for template_file_name in template_file_list:
            template_to_all_options[template_file_name] = get_individual_key_list(template_file_name)
            form["template_options"][template_file_name]["all_options"] = []
            for option in template_to_all_options[template_file_name]:
                item = {}
                option_name = option.name
                option_path = option.path
                item["name"] = option_name
                item["path"] = str(option_path)
                item["value"] = "None"
                form["template_options"][template_file_name]["all_options"].append(item)

            # sort the form["template_options"][template_file_name]["all_options"] based on the name of the item in
            # the list
            form["template_options"][template_file_name]["all_options"] = sorted(form["template_options"][template_file_name]["all_options"], key=lambda x: x["name"])

        # output the form to a yaml file in the exp path
        form_file_path = os.path.join(exp_path, "form.yaml")
        with open(form_file_path, "w") as f:
            yaml.dump(form, f, Dumper=yaml.Dumper, sort_keys=False)

        create_form(exp_name)

        # create a form_variable.py file wiht a def return_variables() function that returns []
        # also scaling that returns [
        form_variable_file_path = os.path.join(exp_path, "form_variable.py")
        # check if the file exists
        if not os.path.exists(form_variable_file_path):
            with open(form_variable_file_path, "w") as f:
                f.write("# copy the file into admin_input folder and change accordingly\n")
                f.write("# the return_variables() function returns a list of dictionaries\n")
                f.write("# each dictionary is a set of variables that will be used to generate a configuration\n")
                f.write("def return_variables():\n")
                f.write("    return {}\n")
                f.write("def return_scaling():\n")
                f.write("    return [1]\n")
                f.write("def return_optimization_options():\n")
                f.write("    return [[]]\n")

        # copy the template file to the exp_path/template folder
        template_path = os.path.join(exp_path, "template")
        if not os.path.exists(template_path):
            os.mkdir(template_path)
        for template_file_name in template_file_list:
            template_file_path = os.path.join(current_path, "template", template_file_name)
            shutil.copy(template_file_path, template_path)


def create_form(exp_name):
    # copy the template file to the admin_input folder
    # named using timestamp
    current_path = os.path.dirname(os.path.abspath(__file__))
    exp_path = os.path.join(current_path, "exp", exp_name)
    # assert form.yaml exists
    form_file_path = os.path.join(exp_path, "form.yaml")
    form_variable_file_path = os.path.join(exp_path, "form_variable.py")
    assert os.path.exists(form_file_path), "form.yaml does not exist in the exp folder"
    # copy the form.yaml to the admin_input folder
    admin_input_path = os.path.join(exp_path, "admin_input")
    if not os.path.exists(admin_input_path):
        os.mkdir(admin_input_path)
    # check whether there are files in the admin_input folder
    # if there are files, skip the copy
    if len(os.listdir(admin_input_path)) > 0:
        return
    # copy the form.yaml to the admin_input folder
    import shutil
    shutil.copy(form_file_path, admin_input_path)
    # shutil.copy(form_variable_file_path, admin_input_path)
    # rename the form.yaml to the timestamp
    import time
    # timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    # form_file_path = os.path.join(admin_input_path, "form.yaml")
    # new_form_file_path = os.path.join(admin_input_path, timestamp + ".yaml")
    # os.rename(form_file_path, new_form_file_path)


if __name__ == '__main__':

    # generate a list of configuration files
    # input:
    #   a list of template files
    #   some rules to fill out the values in the template files
    # command line
    #  python3 generate_configuration.py exp_name=traffic_generator_testing template_file_list=Machine1_Traffic2_Worker1$template.yaml,Machine1_Traffic2_Worker2$template.yaml,...
    exp_name = ""
    template_file_list = []
    for arg in sys.argv[1:]:
        if arg.startswith("exp_name="):
            exp_name = arg.split("=")[1]
        if arg.startswith("template_file_list="):
            template_file_list = arg.split("=")[1].split(",")

    if exp_name == "":
        exp_name = "traffic_generator_testing"
    if len(template_file_list) == 0:
        template_file_list = [
            "Machine1_Traffic2_Worker1$template.yaml"
        ]

    create_exp({"exp_name": exp_name, "template_file_list": template_file_list})