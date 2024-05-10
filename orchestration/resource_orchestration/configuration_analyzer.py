import pprint

from ontology.parse import get_subdict, filter_dict
from orchestration.resource_orchestration.resource_orchestration import WorkerSetting
from utility import type_to_string


def get_num_queue(input_dict: dict) -> int:
    assert input_dict is not None
    assert type(input_dict) is dict
    # assert input_dict["type"] == type_to_string(Workers)
    return len(input_dict[type_to_string(WorkerSetting)])


def search_path_field_value(input: dict, field, value, path=None) -> list:
    # depth first search
    if path is None:
        path = []
    if field in input:
        if input[field] == value:
            return path
    for key, value_dict in input.items():
        if isinstance(value_dict, dict):
            temp_path = search_path_field_value(input=value_dict, field=field, value=value, path=path + [key])
            if temp_path is not None:
                return temp_path


def get_worker_parameter(worker_config_dict: dict) -> dict:
    return worker_config_dict["WorkerParameters"]


def get_actor_table(worker_config_dict: dict) -> dict:
    nf_definition_dic = (get_subdict(input=worker_config_dict, field="NFDefinition"))
    temp_dic = {}
    for key, value in nf_definition_dic.items():
        if value["is_abstract"] == True:
            continue
        temp_type = value["type"]
        temp_value = key
        temp_dic[temp_value] = temp_type
    return temp_dic



def get_actor_entry_event(worker_config_dict: dict) -> dict:
    actor_dic = (get_subdict(input=worker_config_dict, field="Actor"))
    # pprint.pprint(actor_dic)
    temp_dic = {}
    for key, value in actor_dic.items():
        temp_dic[key] = value["entry_event"]
    return temp_dic

def get_control_state_init_parameters(worker_config_dict: dict) -> list:
    control_state = (get_subdict(input=worker_config_dict, field="ControlState"))
    temp_dic = {}
    temp_dic = control_state.copy()
    del temp_dic[0] # the first control state is for the first nf, which is the system nf, so we delete it?
    for key, value in temp_dic.items():
        if "transition" in value["parameters"]:
            for key1, value1 in value["parameters"]["transition"].items():
                key1 = key1.split(".")[-1] # the split method get the inner event. For example "nf.event" -> "event"
                value["parameters"][key1] = value1
            del value["parameters"]["transition"]
    for key, value in temp_dic.items():
        # value["nftype"] = get_subdict(input=worker_config_dict, field="NFDefinition")[int(value["composed_nf"])]["type"]
        value["control_state_id"] = str(key)
        del value["composed_nf"]

    result_list = []
    for key, value in temp_dic.items():
        temp_list = []
        nftype = value["type"]
        control_state_id = value["control_state_id"]
        temp_list.append(nftype)
        temp_list.append(control_state_id)
        temp_list.append(value["parameters"].copy())
        temp_dict = temp_list[2]
        for key1, value1 in temp_dict.items():
            if type(value1) is dict:
                if "traffic" in key1:
                    continue
                else:
                    del temp_dict[key1]
                    break
        result_list.append(temp_list)
    return result_list


def get_actor_id_control_id_association(worker_config_dict: dict) -> dict:
    actor_dic = get_subdict(input=worker_config_dict, field="Actor")
    actor_id_to_control_id = {}
    for key, value in actor_dic.items():
        actor_id_to_control_id[key] = value["ControlState"]
    return actor_id_to_control_id

def get_actor_id_datablock_id_association(worker_config_dict: dict) -> dict:
    actor_dic = get_subdict(input=worker_config_dict, field="Actor")
    actor_id_to_datablock_id = {}
    for key, value in actor_dic.items():
        actor_id_to_datablock_id[key] = {}
        actor_id_to_datablock_id[key]["datablock_id"] = value["datablock_id"]
        actor_id_to_datablock_id[key]["datablock_offset"] = value["datablock_offset"]
    return actor_id_to_datablock_id

def init_datablocks(worker_config_dict: dict) -> list:
    temp_list = []
    datablock_dic = get_subdict(input=worker_config_dict, field="DataBlock")
    for datablock_id, datablock in datablock_dic.items():
        temp_dict = {}
        datablock_type = datablock["type"]
        control_state_id = datablock["control_state_id"]
        entry_num = datablock["total_entry_num"]
        size = datablock["size"]
        num_flow_differentiated_per_entry = datablock["num_flow_differentiated_per_entry"]
        temp_dict["type"] = datablock_type
        temp_dict["size"] = size
        temp_dict["num_flow_differentiated_per_entry"] = num_flow_differentiated_per_entry
        temp_dict["entry_num"] = entry_num
        temp_dict["control_state_id"] = control_state_id
        temp_dict["datablock_id"] = datablock_id
        temp_list.append(temp_dict)
    return temp_list


if __name__ == '__main__':
    from orchestration import resource_orchestration_data_loader

    config_dic = resource_orchestration_data_loader("test_1")
    workers_config_dict = config_dic["Workers"][0]
    pprint.pprint(workers_config_dict)
    pprint.pprint(get_worker_parameter(workers_config_dict))
    pprint.pprint(get_control_state_init_parameters(workers_config_dict))
    pprint.pprint(get_actor_id_control_id_association(workers_config_dict))
    pprint.pprint(get_actor_id_datablock_id_association(workers_config_dict))
    pprint.pprint(get_actor_table(workers_config_dict))
    pprint.pprint(init_datablocks(workers_config_dict))
