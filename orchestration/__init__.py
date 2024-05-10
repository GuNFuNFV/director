import os

from orchestration.nf_composer import NFComposer, nf_definition_file_loader
from utility.dict_utility import convert_key_value_to_int


def all_nf_definition():
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder_name = "nf_composition"
    nf_definition_file_path = os.path.join(current_path, folder_name)
    # list all the composed_nf_definition_file in the folder
    nf_definition_file_list = os.listdir(nf_definition_file_path)
    file_name_to_file_path = {}
    for file_name in nf_definition_file_list:
        file_path = os.path.join(nf_definition_file_path, file_name)
        file_name_to_file_path[file_name] = file_path
    return file_name_to_file_path

def load_composed_nf(composed_nf_nfd):
    nf_composer = NFComposer()
    nf_composer.compile(composed_nf_nfd)
    return nf_composer


def resource_orchestration_data_loader(file_name):
    # read the configuration file from current directory of this file + composed_nf_definition_file + file_name as
    # json file
    import os
    import json
    file_name = file_name + ".json"
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path, "resource_orchestration/files")
    path = os.path.join(path, file_name)
    with open(path, 'r') as f:
        workers_config_dict = json.load(f)
    workers_config_dict = convert_key_value_to_int(workers_config_dict)
    return workers_config_dict

if __name__ == "__main__":
    print(nf_definition_file_loader("cuckoo_rtc_generic.nfd"))
    print(all_nf_definition())