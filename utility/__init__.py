from copy import deepcopy

from .debug import dprint


def red_print(*args, **kwargs):
    print("\033[1;31;40m", *args, "\033[0m", flush=True, **kwargs)


# red print with no newline
def red_print_n(*args):
    print("\033[1;31;40m", *args, "\033[0m", end="", flush=True)


def dic_to_configuration_string(dic: dict):
    temp_dic = deepcopy(dic)
    for key in dic:
        # if dic[key] is a string, continue
        if isinstance(dic[key], str):
            continue
        # if it is a function, evaluate it
        if callable(dic[key]):
            temp_dic[key] = dic[key]()
    json_string = str(temp_dic)
    json_string = json_string.replace("{", "")
    json_string = json_string.replace("}", "")
    json_string = json_string.replace('"', "")
    json_string = json_string.replace(":", "")
    json_string = json_string.replace(",", "")
    json_string = json_string.replace("'", "")
    json_string = json_string.replace(" ", "$")
    del temp_dic
    return json_string


from .parameters import *
from .functional_utility import *
from .debug import *


def type_to_string(temp_type: type):
    temp_type_name = str(temp_type)
    # split by the '
    temp_type_name = temp_type_name.split("'")[1]
    # split by the .
    temp_type_name = temp_type_name.split(".")[1:]
    return temp_type_name[-1]


from .file_io import read_file_from_folder
from .tree_from_dic import Tree
